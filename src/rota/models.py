import pickle
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any

from dateutil.rrule import rrule
from django.db import models
from django.core.exceptions import ValidationError

from django.conf import settings

class RSVPChoices(models.TextChoices):
    YES = 'yes', 'Yes'
    NO = 'no', 'No'
    CANT_MAKE_IT = 'cmi', 'Can\'t make it'
    NONE = '-', 'No Response'

class SupervisorAccessRoleChoices(models.TextChoices):
    ALL_ORG = 'all_org', 'All Organisation Shifts'
    ALL_OPPORTUNITY = 'all_opportunity', 'All Shifts for given Opportunities'
    ALL_ROLE = 'all_role', 'All shift for given roles'
    SPECIFIC_SHIFTS = 'specific_shifts', 'Specific shifts'

class Schedule(models.Model):
    opportunity = models.ForeignKey('opportunities.Opportunity', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    start_date = models.DateField()
    end_date = models.DateField()

    start_time = models.TimeField()
    end_time = models.TimeField()

    recurrence_rule = models.BinaryField(blank=True, null=True)

    def clean(self) -> None:
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")

    def is_recurring(self) -> bool:
        return self.recurrence_rule is not None

    def set_rrule(self, **kwargs: Any) -> None:
        """
        Accepts rrule constructor kwargs, sets recurrence_rule field.
        """
        dtstart: datetime = datetime.combine(self.start_date, self.start_time)
        until: datetime = datetime.combine(self.end_date, self.end_time)

        kwargs.setdefault('dtstart', dtstart)
        kwargs.setdefault('until', until)

        rule: rrule = rrule(**kwargs)
        self.recurrence_rule = pickle.dumps(rule)

    def get_rrule(self) -> Optional[rrule]:
        if not self.recurrence_rule:
            return None
        return pickle.loads(self.recurrence_rule)

    def get_occurrences(self) -> List[Dict[str, Any]]:
        if not self.is_recurring():
            return [{
                'date': self.start_date,
                'start_time': self.start_time,
                'end_time': self.end_time,
            }]

        rule: Optional[rrule] = self.get_rrule()
        if not rule:
            return []

        return [{
            'date': dt.date(),
            'start_time': self.start_time,
            'end_time': self.end_time,
        } for dt in rule]


class Role(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    volunteer_description = models.TextField(blank=True, default='')
    required_volunteers = models.IntegerField()
    opportunity = models.ForeignKey("opportunities.Opportunity", on_delete=models.CASCADE)

    def __str__(self):
        return self.opportunity.name + " - " + self.name

    def get_volunteers(self):
        sections = Section.objects.filter(role=self)
        if sections.exists():
            return sections.aggregate(total=models.Sum('required_volunteers'))['total']
        else:
            return self.required_volunteers


class Section(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    required_volunteers = models.IntegerField()
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

class VolunteerScheduleAvailability(models.Model):
    registration = models.ForeignKey('opportunities.Registration', on_delete=models.CASCADE)
    schedule = models.ForeignKey('rota.Schedule', on_delete=models.CASCADE)

class VolunteerOneOffDateAvailability(models.Model):
    registration = models.ForeignKey('opportunities.Registration', on_delete=models.CASCADE)
    one_off_date = models.ForeignKey('rota.OneOffDate', on_delete=models.CASCADE)

class VolunteerRoleIntrest(models.Model):
    registration = models.ForeignKey('opportunities.Registration', on_delete=models.CASCADE)
    role = models.ForeignKey('rota.Role', on_delete=models.CASCADE)

class Occurrence(models.Model):
    schedule = models.ForeignKey('rota.Schedule', on_delete=models.CASCADE, blank=True, null=True, unique=True)
    one_off_date = models.ForeignKey('rota.OneOffDate', on_delete=models.CASCADE, blank=True, null=True, unique=True)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def clean(self) -> None:
        if self.schedule and self.one_off_date:
            raise ValidationError("Only one off or schedule date can be specified.")

        if self.one_off_date:
            self.date = self.one_off_date.date
            self.start_time = self.one_off_date.start_time
            self.end_time = self.one_off_date.end_time

    def __str__(self):
        return f"{self.one_off_date.opportunity}{f' - {self.one_off_date.role.name}' if self.one_off_date.role else ''} - {self.date} ({self.start_time} - {self.end_time})"


class VolunteerShift(models.Model):
    registration = models.ForeignKey('opportunities.Registration', on_delete=models.CASCADE, null=True)

    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE)
    role = models.ForeignKey('rota.Role', on_delete=models.CASCADE)

    section = models.ForeignKey('rota.Section', on_delete=models.CASCADE, blank=True, null=True)

    confirmed = models.BooleanField(default=False)

    check_in_time = models.TimeField(blank=True, null=True)
    check_out_time = models.TimeField(blank=True, null=True)

    rsvp_response = models.CharField(
        max_length=10,
        choices=RSVPChoices.choices,
        default=RSVPChoices.NONE,
    )

    rsvp_reason = models.CharField(blank=True, null=True, max_length=255)

    def status(self):
        return self.registration.get_registration_status()

    class Meta:
        unique_together = ('registration', 'occurrence')


class OneOffDate(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    opportunity = models.ForeignKey('opportunities.Opportunity', on_delete=models.CASCADE)

    #allow optional role to be defined, which mean this schedule is only for
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, default=None, blank=True)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")


class Supervisor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organisation = models.ForeignKey('organisations.Organisation', on_delete=models.CASCADE)

    access_level = models.CharField(
        max_length=20,
        choices=SupervisorAccessRoleChoices.choices,
        default=SupervisorAccessRoleChoices.SPECIFIC_SHIFTS,
    )

    supervisor_opportunities = models.ManyToManyField('opportunities.Opportunity', blank=True)
    supervisor_roles = models.ManyToManyField(Role, blank=True)
    supervisor_shifts = models.ManyToManyField(Occurrence, blank=True)

    class Meta:
        unique_together = ('user', 'organisation')