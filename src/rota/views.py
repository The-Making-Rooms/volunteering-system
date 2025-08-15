from django.shortcuts import render

from commonui.views import check_if_hx
from opportunities.models import Registration
from rota.models import Occurrence, VolunteerShift
from datetime import datetime


# Create your views here.
def shift_supervisor(request, occurrence_id):
    occurrence = Occurrence.objects.get(id=occurrence_id)


    shifts = VolunteerShift.objects.filter(
        occurrence = occurrence,
        confirmed=True
    )

    shifts = [shift for shift in shifts if shift.status() == "active"]

    context = {
        'hx' : check_if_hx(request),
        'shifts' : shifts,
        'occurrence' : occurrence
    }

    return render(request, 'rota/role_screen.html', context)

def checkin_shift(request, shift_id):



    shift = VolunteerShift.objects.get(id=shift_id)


    if not shift.check_in_time:
        shift.check_in_time = datetime.now().time()
        shift.save()
    elif not shift.check_out_time:
        shift.check_out_time = datetime.now().time()
        shift.save()

    return shift_supervisor(request, shift.occurrence.id)
