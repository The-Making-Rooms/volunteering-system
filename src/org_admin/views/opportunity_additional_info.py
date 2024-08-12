from django.shortcuts import render
from commonui.views import check_if_hx
from .common import check_ownership
from .opportunity_details import opportunity_details, opportunity_admin_list
from opportunities.models import Opportunity,  SupplimentaryInfoRequirement
from volunteer.models import SupplementaryInfo
from ..models import OrganisationAdmin

def opportunity_supplementary_info(request, opp_id):
    if request.method == "POST":
        opportunity = Opportunity.objects.get(id=opp_id)
        if not check_ownership(request, opportunity):
            request.method = "GET"
            return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
        
        try:
            supp_id = request.POST["supp_id"]
            
            if supp_id == "":
                request.method = "GET"
                return opportunity_details(request, opp_id, error="Supplementary Info cannot be empty. Use organisation details to add new information.", tab_name="details")
            
            supp_info = SupplementaryInfo.objects.get(id=supp_id)
            info_req = SupplimentaryInfoRequirement(
                opportunity=opportunity,
                info=supp_info,
            )
            info_req.save()
        except SupplementaryInfo.DoesNotExist:
            request.method = "GET"
            return opportunity_admin_list(request, error="Supplementary Info does not exist")
        except Exception as e:
            print(e)
            request.method = "GET"
            return opportunity_admin_list(request, error=e)
        
        context = {
            "hx": check_if_hx(request),
            "supp_info": supp_info,
            "opportunity": opportunity,
        }
        
        request.method = "GET"
        return opportunity_details(request, opp_id, success="Supplementary Info added successfully", tab_name="details")
    else:
        opportunity = Opportunity.objects.get(id=opp_id)
        if not check_ownership(request, opportunity):
            return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
        

        supp_infos = SupplimentaryInfoRequirement.objects.filter(opportunity=opportunity)
        unavail_ids = [supp_info.info.id for supp_info in supp_infos]
        
        if not request.user.is_superuser:
            avail_supp_infos = SupplementaryInfo.objects.filter(organisation=OrganisationAdmin.objects.get(user=request.user).organisation).exclude(id__in=unavail_ids)
        else:
            avail_supp_infos = SupplementaryInfo.objects.filter(organisation=opportunity.organisation).exclude(id__in=unavail_ids)
        
        context = {
            "hx": check_if_hx(request),
            "opportunity": opportunity,
            "supp_infos": supp_infos,
            "avail_supp_infos": avail_supp_infos,
        }
        
        return render(request, "org_admin/partials/oppportunity_additional_info.html", context)
    
def delete_info_req(request, supp_id):
    supp = SupplimentaryInfoRequirement.objects.get(id=supp_id)
    opp = supp.opportunity
    
    if not check_ownership(request, opp):
        return opportunity_admin_list(request, error="You do not have permission to view this opportunity")
    
    supp.delete()
    
    return opportunity_details(request, opp, success="Supplementary Info deleted successfully")