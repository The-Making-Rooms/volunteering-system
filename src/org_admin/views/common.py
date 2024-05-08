from ..models import OrganisationAdmin

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