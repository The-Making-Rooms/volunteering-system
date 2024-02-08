from django.http import HttpResponse
from django.shortcuts import render
from opportunities.models import Opportunity, Benefit, Image, Video, SupplimentaryInfoRequirement, Registration
from volunteer.models import SupplementaryInfo, SupplementaryInfoGrantee, VolunteerSupplementaryInfo, Volunteer
from django.template import loader

from commonui.views import check_if_hx

# Create your views here.
def detail(request, opportunity_id):
    #print(opportunity_id)
    template = loader.get_template("opportunities/opportunity-details.html")
    opportunity = Opportunity.objects.get(id=opportunity_id)
    benefits = Benefit.objects.filter(opportunity=opportunity)
    text_rules_inclusion = []

    opp_images = Image.objects.filter(opportunity=opportunity)
    opp_videos = Video.objects.filter(opportunity=opportunity)

    for rule in opportunity.recurrences.rrules:
        text_rules_inclusion.append(rule.to_text())

    context = {
        "opportunity": opportunity,
        "benefits": benefits,
        "text_rules_inclusion": text_rules_inclusion,
        "opp_images": opp_images,
        "opp_videos": opp_videos,
        "hx" : check_if_hx(request)
    }

    return HttpResponse(template.render(context, request))

def register(request, opportunity_id):
    opportunity = Opportunity.objects.get(id=opportunity_id)
    supp_reqs = SupplimentaryInfoRequirement.objects.filter(opportunity=opportunity)
    supp_infos = VolunteerSupplementaryInfo.objects.filter(volunteer=Volunteer.objects.get(user=request.user))
    context = {
        "opportunity": opportunity,
        "hx": check_if_hx(request),
        "supp_reqs": supp_reqs,
        "supp_infos": supp_infos
    }
    return render(request, 'opportunities/register.html', context=context)