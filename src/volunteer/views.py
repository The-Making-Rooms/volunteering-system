from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from volunteer.models import Volunteer, VolunteerAddress
from django.core.exceptions import ObjectDoesNotExist
import random
from datetime import datetime
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
    
def createVolunteer(data, user):
    print(data['DateOfBirth'])
    new_volunteer = Volunteer(
        user = user,
        #avatar = models.ImageField(upload_to='avatars/')
        date_of_birth = datetime.strptime(data['DateOfBirth'], '%Y-%m-%d'),
        phone_number = data['PhoneNumber'],
        bio = '',
        #CV = models.FileField(upload_to='CV/', blank=True)
    )

    new_volunteer.save()

    volunteerAddress = VolunteerAddress(
        first_line = data['inputAddress'],
        second_line = data['inputAddress2'],
        postcode = data['postCode'],
        city = data['city'],
        volunteer = new_volunteer,
    )

    volunteerAddress.save()

def emergencyContactInput(request):
    match request.method:
        case 'GET':
            try:
                validPath = request.headers['HX-Current-URL'].split('/')[-2] == 'volunteer'
            except KeyError:
                return HttpResponseRedirect('/volunteer')
            if validPath:
                random_key = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
                print(random_key)
                return render(request,
                               'volunteer/emergency-contact-form.html',
                               {
                                   'name': 'name-'+random_key,
                                   'email': 'email-'+random_key,
                                   'phone': 'phone-'+random_key,
                                   'relationship': 'relation-'+random_key,
                               })
            else:
                return HttpResponseRedirect('/volunteer')


def emergencyContactForm(request):
    print(request.method)

    match request.method:
        case 'GET':
            try:
                validPath = request.headers['HX-Current-URL'].split('/')[-2] == 'volunteer'
            except KeyError:
                return HttpResponseRedirect('/volunteer')
            if validPath:
                return render(request, 'volunteer/emergency-contacts.html')
            else:
                return HttpResponseRedirect('/volunteer')
        case 'POST':
            data = request.POST
            print(data)
            request.method = 'GET' #Change the requst method so the next function renders instead of trying to parse the data
            return 

def coreInfoForm(request):
    match request.method: #Handle request types
        case 'GET': #GET request
            try:
                validPath = request.headers['HX-Current-URL'].split('/')[-2] == 'volunteer' #Should only be coming from the initial URL view, swapped by HTMX
            except KeyError:
                return HttpResponseRedirect('/volunteer') #Redirect if incorrectly accessed
            if validPath:
                return render(request, 'volunteer/core-info.html') #Return form if correct
            else:
                return HttpResponseRedirect('/volunteer')  #Could be coming from HTMX but not from the correct URL
        case 'POST':
            data = request.POST
            print(data)
            createVolunteer(data, request.user)
            request.method = 'GET' #Change the requst method so the next function renders instead of trying to parse the data
            return (emergencyContactForm(request))

