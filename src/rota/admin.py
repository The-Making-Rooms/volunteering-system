from django.contrib import admin

from opportunities.models import Tag
from rota.models import Occurrence, Schedule, VolunteerShift, Role

# Register your models here.
admin.site.register(Occurrence)
admin.site.register(Schedule)
admin.site.register(VolunteerShift)
admin.site.register(Role)