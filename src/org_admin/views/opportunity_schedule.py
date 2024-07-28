from opportunities.models import Opportunity
import recurrence
from django.shortcuts import render
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from .opportunity_details import opportunity_details, opportunity_admin_list
from .common import check_ownership
import datetime


def manage_schedule(request, id):
    if request.method == "GET":
        
 
        try:
            opp = Opportunity.objects.get(id=id)
        except Opportunity.DoesNotExist:
            return opportunity_admin_list(request, error="Opportunity does not exist")
        
        
        try:
            reccurances = opp.recurrences.rrules[0].freq
            start_date = opp.recurrences.dtstart
            end_date = opp.recurrences.dtend
        except AttributeError:
            reccurances = 'none'
            start_date = None
            end_date = None
        except IndexError:
            reccurances = 'none'
            start_date = None
            end_date = None
        
            
        try:
            individual_dates = opp.recurrences.rdates
        except AttributeError:
            individual_dates = []
        except IndexError:
            individual_dates = []
            
        context = {
            "hx": check_if_hx(request),
            "opportunity": opp,
            "recurrences": reccurances,
            "start_date": start_date,
            "end_date": end_date,
            "individual_dates": individual_dates,
        }
        
        return render(request, "org_admin/partials/opportunity_schedule.html", context=context)
    
    if request.method == "POST":
        data = request.POST
        opportunity = Opportunity.objects.get(id=id)
        
        #Start and end times
        start_time = datetime.datetime.strptime(data["start_time"], "%H:%M")
        end_time = datetime.datetime.strptime(data["end_time"], "%H:%M")
        opportunity.start_time = start_time
        opportunity.end_time = end_time
        
        #Set start and end dates
        if data["recurrences"] != "never":
            
            try:
                start_date = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d")
                end_date = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d")
            except ValueError:
                request.method = "GET"
                return opportunity_details(request, id, error="Please select a start and end date", tab_name="schedule")
            
            opportunity.recurrences.dtstart = start_date
            opportunity.recurrences.dtend = end_date
            
            if start_date > end_date:
                return opportunity_details(request, id, error="Start date must be before end date")
            
            if start_time > end_time:
                return opportunity_details(request, id, error="Start time must be before end time")
            
            
        #Set recurrance frequency   
        if data["recurrences"] == "never":
            if len(opportunity.recurrences.rdates) > 0:
                opportunity.recurrences.rrules = []
            else:
                request.method = "GET"
                return opportunity_details(request, id, error="Please add dates or select a recurrence frequency", tab_name="schedule")
            
        elif data["recurrences"] == "daily":
            opportunity.recurrences.rrules = [recurrence.Rule(recurrence.DAILY)]
        elif data["recurrences"] == "weekly":
            day_name = start_date.strftime("%w")
            opportunity.recurrences.rrules = [recurrence.Rule(recurrence.WEEKLY, byday=[int(day_name)-1])]
        elif data["recurrences"] == "monthly":
            opportunity.recurrences.rrules = [recurrence.Rule(recurrence.MONTHLY)]
        elif data["recurrences"] == "yearly":
            opportunity.recurrences.rrules = [recurrence.Rule(recurrence.YEARLY)]
            
        opportunity.save()
        
        request.method = "GET"
        return opportunity_details(request, id, success="Schedule updated", tab_name="schedule")
        
def delete_date(request, id, opportunity_id):
    opp = Opportunity.objects.get(id=opportunity_id)
    if check_ownership(request, opp):
        opp.recurrences.rdates.remove(opp.recurrences.rdates[id])
        opp.save()
    else:
        return opportunity_details(request, opportunity_id, error="You do not have permission to delete this date", tab_name="schedule")
    
    return opportunity_details(request, opportunity_id, success="Date deleted", tab_name="schedule")

def add_date(request, id):
    if request.method == "POST":
        data = request.POST
        opp = Opportunity.objects.get(id=id)
        if check_ownership(request, opp):
            recurrence_type = type(opp.recurrences)
            if recurrence_type != recurrence.Recurrence:
                opp.recurrences = recurrence.Recurrence()
            opp.recurrences.rdates.append(datetime.datetime.strptime(data["date"], "%Y-%m-%d"))
            opp.save()
        else:
            request.method = "GET"
            return opportunity_details(request, id, error="You do not have permission to add a date", tab_name="schedule")
        
        request.method = "GET"
        return opportunity_details(request, id, success="Date added", tab_name="schedule")
    else:
        return render(
            request,
            "org_admin/partials/add_date.html",
            {"hx": check_if_hx(request), "opportunity_id": id},
        )