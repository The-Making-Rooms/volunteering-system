from organisations.models import Link, LinkType, Organisation
from org_admin.models import OrganisationAdmin
from .views import details

def org_links(request, organisation_id=None):
    if request.method == "POST":
        if request.user.is_superuser and organisation_id:
            organisation = Organisation.objects.get(id=organisation_id)
        elif request.user.is_superuser:
            return details(request, error="Organisation not found") 
        else:
            organisation = OrganisationAdmin.objects.get(user=request.user).organisation
        
        data = request.POST
        link_types = LinkType.objects.all()
        for key in data:
            if key.startswith("type_"):
                link_type_id = key.split("_")[1]
                curr_type = link_types.get(id=link_type_id)
                if data[key] == "":
                    try:
                        link = Link.objects.get(organisation=organisation, link_type=curr_type)
                        link.delete()
                    except Link.DoesNotExist:
                        pass
                else:
                    try:
                        link = Link.objects.get(organisation=organisation, link_type=curr_type)
                        link.url = data[key]
                        link.save()
                    except Link.DoesNotExist:
                        link = Link.objects.create(organisation=organisation, link_type=curr_type, url=data[key])
                        link.save()
        request.method = "GET"
        return details(request, organisation_id=organisation.id)
                    
    