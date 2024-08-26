from ..models import OrganisationAdmin

import datetime

def check_schedule_dates(opportunity):
    dates = opportunity.recurrences.after(datetime.datetime.now())
    ind_dates = opportunity.recurrences.rdates
    
    rdates_have_future = False
    
    for date in ind_dates:
        if date > datetime.datetime.now():
            rdates_have_future = True
            break
    
    if dates == None and not rdates_have_future:
        return False
    return True

def check_ownership(request, entity):
    if request.user.is_superuser:
        return True
    try:
        if (
            entity.organisation
            != OrganisationAdmin.objects.get(user=request.user).organisation
        ):
            return False
        else:
            return True
    except AttributeError:
        if entity.opportunity.organisation != OrganisationAdmin.objects.get(
            user=request.user
        ).organisation:
            return False
        else:
            return True