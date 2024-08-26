from volunteer.models import Volunteer, MentorRecord, MentorSession, MentorNotes
from org_admin.models import OrganisationAdmin
from opportunities.models import Registration
from django.shortcuts import render
from commonui.views import check_if_hx
from .common import check_ownership
from datetime import datetime, timedelta
from forms.models import Form, Response
from forms.views import fill_form

def get_mentees(request):
    if request.user.is_superuser:
        org_mentees = MentorRecord.objects.all()
        print(org_mentees)
        available_to_mentor = None
    else:
        org = OrganisationAdmin.objects.get(user=request.user)
        org_volunteers = Registration.objects.filter(opportunity__organisation=org.organisation).values_list('volunteer', flat=True).distinct()
        
        #Get all volunteers mentor records, regardless if that organisation created it. The edit capability will be handled fontend.
        org_mentees = MentorRecord.objects.filter(volunteer__in=org_volunteers)
        available_to_mentor = Volunteer.objects.filter(id__in=org_volunteers).exclude(id__in=org_mentees.values_list('volunteer', flat=True))
        
    context = {
        "hx": check_if_hx(request),
        "mentees": org_mentees,
        "available_to_mentor": available_to_mentor,
        "org" : org if not request.user.is_superuser else None,
        "superuser": request.user.is_superuser
    }
    
    return render(request, "org_admin/mentoring.html", context=context)
        
def create_mentee(request, volunteer_id):
    volunteer = Volunteer.objects.get(id=volunteer_id)
    if Registration.objects.filter(volunteer=volunteer, opportunity__organisation=OrganisationAdmin.objects.get(user=request.user).organisation).count() == 0:
        return render(request, "org_admin/mentoring.html", context={"error": "Volunteer has no registrations"})
    else:
        record = MentorRecord(volunteer=volunteer, organisation=OrganisationAdmin.objects.get(user=request.user).organisation)
        record.save()
        return manage_mentee(request, record.id)
        
def manage_mentee(request, mentee_id):
    mentee_record = MentorRecord.objects.get(id=mentee_id)
    if check_ownership(request, mentee_record):
        mentee = mentee_record.volunteer
        sessions = MentorSession.objects.filter(mentor_record=mentee_record)
        notes = MentorNotes.objects.filter(MentorRecord=mentee_record)
        context = {
            "hx": check_if_hx(request),
            "mentee": mentee,
            "mentee_record": mentee_record,
            "mentor_sessions": sessions,
            "mentor_notes": notes,
        }
        return render(request, "org_admin/mentee_management.html", context=context)
    
def edit_hours(request, session_id):
    session = MentorSession.objects.get(id=session_id)
    if check_ownership(request, session.mentor_record):
        if request.method == "POST":
            
            session_duration_HH = str(session.time).split(":")[0] if len(str(session.time).split(":")[0]) == 2 else "0" + str(session.time).split(":")[0]
            session_duration_MM = str(session.time).split(":")[1] if len(str(session.time).split(":")[1]) == 2 else "0" + str(session.time).split(":")[1]
            
            session_duration_HH_MM = session_duration_HH + ":" + session_duration_MM
            
            if len (request.POST['session_notes']) == 0:
                context = {
                    "hx": check_if_hx(request),
                    "mentee": session.mentor_record.volunteer,
                    "mentee_record": session.mentor_record,
                    "error": "Note cannot be empty",
                    "session": session,
                    "session_duration_HH_MM": session_duration_HH_MM,
                    "edit": True
                }
                return render(request, "org_admin/add_mentor_session.html", context=context)
            
            print(request.POST['time'])
            
            if request.POST['time'] == "00:00":
                context = {
                    "hx": check_if_hx(request),
                    "mentee": session.mentor_record.volunteer,
                    "mentee_record": session.mentor_record,
                    "error": "Duration cannot be 0",
                    "session": session,
                    "session_duration_HH_MM": session_duration_HH_MM,
                    "edit": True
                }
                return render(request, "org_admin/add_mentor_session.html", context=context)
            
            time = request.POST['time'].split(":")
            time = timedelta(hours=int(time[0]), minutes=int(time[1]))
            session.time = time
            session.date = request.POST['date']
            session.session_notes = request.POST['session_notes']
            session.save()
            request.method = "GET"
            return manage_mentee(request, session.mentor_record.id)
        else:
            
            #Session duration in HH:MM format, padded with 0s
            
            session_duration_HH = str(session.time).split(":")[0] if len(str(session.time).split(":")[0]) == 2 else "0" + str(session.time).split(":")[0]
            session_duration_MM = str(session.time).split(":")[1] if len(str(session.time).split(":")[1]) == 2 else "0" + str(session.time).split(":")[1]
            
            session_duration_HH_MM = session_duration_HH + ":" + session_duration_MM
            
            
            context = {
                "hx": check_if_hx(request),
                "mentee": session.mentor_record.volunteer,
                "mentee_record": session.mentor_record,
                "session": session,
                "session_duration_HH_MM": session_duration_HH_MM,
                "edit": True
            }
            return render(request, "org_admin/add_mentor_session.html", context=context)
        
def delete_hours(request, session_id):
    session = MentorSession.objects.get(id=session_id)
    if check_ownership(request, session.mentor_record):
        session.delete()
        return manage_mentee(request, session.mentor_record.id)
    
def log_hours(request, mentee_id):
    mentee_record = MentorRecord.objects.get(id=mentee_id)
    if check_ownership(request, mentee_record):
        if request.method == "POST":
            
            #Convert post['time'] to a timedelta object. Format is HH:MM
            time = request.POST['time'].split(":")
            time = timedelta(hours=int(time[0]), minutes=int(time[1]))
            
            print(mentee_record)
            
            session = MentorSession(
                mentor_record=mentee_record, 
                mentor_user=request.user,
                time=time, 
                date=request.POST['date'], 
                session_notes=request.POST['session_notes']
                )
            
            session.save()
            
            request.method = "GET"
            return manage_mentee(request, mentee_id)
        else:
            context={
                "mentee": mentee_record.volunteer,
                "date": datetime.now().date(),
                "mentee_record": mentee_record,
            }
            return render(request, "org_admin/add_mentor_session.html", context=context)
        
def add_note(request, mentee_id):
    mentee_record = MentorRecord.objects.get(id=mentee_id)
    if check_ownership(request, mentee_record):
        if request.method == "POST":
            
            if len (request.POST['session_notes']) == 0:
                context = {
                    "hx": check_if_hx(request),
                    "mentee": mentee_record.volunteer,
                    "mentee_record": mentee_record,
                    "error": "Note cannot be empty"
                }
                return render(request, "org_admin/add_mentor_note.html", context=context)
            
            note = MentorNotes(
                MentorRecord=mentee_record,
                note=request.POST['session_notes'],
                created_by=request.user)
            note.save()
            return manage_mentee(request, mentee_id)
        else:
            context={
                "hx": check_if_hx(request),
                "mentee": mentee_record.volunteer,
                "mentee_record": mentee_record,
            }
            return render(request, "org_admin/add_mentor_note.html", context=context)


def fill_entry_form(request, mentee_id):
    
    try:
        mentoring_start_form = Form.objects.get(name="Mentoring Start Form")
    except Form.DoesNotExist:
        return render(request, "org_admin/mentoring.html", context={"error": "No mentoring start form found. Contact Admin"})

    mentee_record = MentorRecord.objects.get(id=mentee_id)

    form_filled = Response.objects.filter(form=mentoring_start_form, user=mentee_record.volunteer.user).count() > 0
    
    if form_filled:
        return render(request, "org_admin/mentoring.html", context={"error": "Form already filled"})
    else:
        return fill_form(request, mentoring_start_form.id, True)