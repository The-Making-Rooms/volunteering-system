from django.http import HttpResponse
from django.shortcuts import render
from opportunities.models import Opportunity, Benefit
from django.template import loader

from commonui.views import check_if_hx

# Create your views here.
def detail(request, opportunity_id):
    #print(opportunity_id)
    template = loader.get_template("opportunities/opportunity-details.html")
    opportunity = Opportunity.objects.get(id=opportunity_id)
    benefits = Benefit.objects.filter(opportunity=opportunity)
    text_rules_inclusion = []

    for rule in opportunity.recurrences.rrules:
        text_rules_inclusion.append(rule.to_text())

    context = {
        "opportunity": opportunity,
        "benefits": benefits,
        "text_rules_inclusion": text_rules_inclusion,
        "hx" : check_if_hx(request)
    }

    return HttpResponse(template.render(context, request))