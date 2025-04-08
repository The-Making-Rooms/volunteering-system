from ..models import OrganisationAdmin
from opportunities.models import Registration, OpportunityView
from communications.models import Message
from django.shortcuts import render
from.auth import sign_in
from commonui.views import check_if_hx
import datetime

def index(request, error=None):
    print("index")
    if not request.user.is_authenticated:
        return sign_in(request)
    try:
        if not request.user.is_superuser:
            try:
                orgnaisation = OrganisationAdmin.objects.get(user=request.user)
            except OrganisationAdmin.DoesNotExist:
                return render(request, "org_admin/no_admin.html", {"hx": check_if_hx(request)})
            
            total_volunteers = Registration.objects.filter(opportunity__organisation=orgnaisation.organisation).count()
            #past 24 hours views
            total_views = OpportunityView.objects.filter(opportunity__organisation=orgnaisation.organisation, time__gte=datetime.datetime.now()-datetime.timedelta(days=1)).count()
            #past 24 hours mesages
            messages= Message.objects.filter(chat__organisation=orgnaisation.organisation, timestamp__gte=datetime.datetime.now()-datetime.timedelta(days=1)).count()
        elif request.user.is_superuser:
            orgnaisation = OrganisationAdmin.objects.all()
            total_volunteers = Registration.objects.all().count()
            #past 24 hours views
            total_views = OpportunityView.objects.filter(time__gte=datetime.datetime.now()-datetime.timedelta(days=1)).count()
            #past 24 hours mesages
            messages= Message.objects.filter(timestamp__gte=datetime.datetime.now()-datetime.timedelta(days=1)).count()
    except OrganisationAdmin.DoesNotExist:
        return render(request, "org_admin/no_admin.html", {"hx": check_if_hx(request)})

    
    
    if request.user.is_superuser:
    
        context = {
            "hx": check_if_hx(request),
            "error": error,
            "organisation": None,
            "total_volunteers": total_volunteers,
            "total_views": total_views,
            "superuser": True,
            }
    else:
        context = {
            "hx": check_if_hx(request),
            "error": error,
            "organisation": orgnaisation.organisation,
            "total_volunteers": total_volunteers,
            "total_views": total_views,
            "messages": messages,
            }

    return render(
        request,
        "org_admin/index.html",
        context=context
    )