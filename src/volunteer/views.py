from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from volunteer.models import Volunteer
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        current_user = request.user
        try:
            volunteer_profile = Volunteer.objects.get(user=current_user)
            print(volunteer_profile)
            return HttpResponse('Profile Found.. Loading ' + current_user.id)
                    
        except ObjectDoesNotExist:
            return render(request, 'volunteer/container.html')
    else:
        return HttpResponse('Not logged in')
    

def emergencyContactForm(request):
    print(request.method)

    match request.method:
        case 'GET':
            try:
                validPath = request.headers['HX-Current-URL'].split('/')[-2] == 'volunteer'
            except KeyError:
                return HttpResponseRedirect('/volunteer')
            if validPath:
                return render(request, 'volunteer/conditions.html')
            else:
                return HttpResponseRedirect('/volunteer')
        case 'POST':
            data = request.POST
            print(data)
            return 

def coreInfoForm(request):
    match request.method: #Handle request types
        case 'GET': #GET request
            try:
                validPath = request.headers['HX-Current-URL'].split('/')[-2] == 'volunteer' #
            except KeyError:
                return HttpResponseRedirect('/volunteer')
            if validPath:
                return render(request, 'volunteer/core-info.html')
            else:
                return HttpResponseRedirect('/volunteer')
        case 'POST':
            data = request.POST
            print(data)
            request.method = 'GET' #Change the requst method so the next function renders instead of trying to parse the data
            return (emergencyContactForm(request))

