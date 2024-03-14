from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from volunteer.models import Volunteer, VolunteerAddress, EmergencyContacts, VolunteerConditions
from opportunities.models import Registration
from django.core.exceptions import ObjectDoesNotExist
import random
from django.contrib.auth.decorators import login_required
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import logout

# Create your views here.

def check_valid_origin(func, expected_url_end, redirect_path):
    def inner(request):
        match request.method:
            case 'GET':
                try:
                    validPath = request.headers['HX-Current-URL'].split('/')[-2] == expected_url_end
                except KeyError:
                    return HttpResponseRedirect(redirect_path)
                if validPath:
                    func()
                else:
                    return HttpResponseRedirect(redirect_path)
        return inner()


def index(request):
    if request.user.is_authenticated:
        current_user = request.user
        try:
            volunteer_profile = Volunteer.objects.get(user=current_user)
            print(volunteer_profile)

            context = {
                'hx': check_if_hx(request),
                'volunteer': volunteer_profile,
                'user': current_user,
                'emergency_contacts': EmergencyContacts.objects.filter(volunteer=volunteer_profile),
                'addresses': VolunteerAddress.objects.filter(volunteer=volunteer_profile),
                'conditions': VolunteerConditions.objects.filter(volunteer=volunteer_profile),
                'registrations': Registration.objects.filter(user=current_user),
                'link_active': 'volunteer',
            }

            return render(request, 'volunteer/index.html', context=context)
                    
        except ObjectDoesNotExist:
            return render(request, 'volunteer/container.html', {'hx': check_if_hx(request)})
        except Exception as e:
            print(e)

    else:
        return render(request, 'commonui/not_logged_in.html', {'hx': check_if_hx(request)})
    
def createVolunteer(data, user):
    print(data['DateOfBirth'])

    user.first_name = data['FirstName']
    user.last_name = data['LastName']
    user.save()

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

def create_emergency_contacts(user, data):
    volunteer_profile = Volunteer.objects.get(user=user)

    print(len(data))

    if len(data) > 1:
        n_contacts = int((len(data)-1)/4)
        print(n_contacts)

        for x in range (1,n_contacts+1):
            start_index = ((x*4) - 4)
            print(x, start_index, start_index+3)
            new_contact = EmergencyContacts(
            name = list(data.values())[start_index],
            relation = list(data.values())[start_index+1],
            phone_number = list(data.values())[start_index+2],
            email = list(data.values())[start_index+3],
            volunteer = volunteer_profile,
            )
            new_contact.save()
    else:
        return


@login_required()
def emergencyContactInput(request):#This is a partial which represents the 'add contact' cards on the onboarding screen
    match request.method:
        case 'GET':
            try:
                validPath = request.headers['HX-Current-URL'].split('/')[-2] == 'volunteer'
            except KeyError:
                return HttpResponseRedirect('/volunteer')
            if validPath:
                random_key = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
                print(random_key) #HTML forms need unique key names, otherwise the data will be combined
                return render(request,
                               'volunteer/emergency-contact-form.html', #This is not the complete form, ONLY the partial
                               {
                                   'name': 'name-'+random_key,
                                   'email': 'email-'+random_key,
                                   'phone': 'phone-'+random_key,
                                   'relationship': 'relation-'+random_key,
                               })
            else:
                return HttpResponseRedirect('/volunteer')
            

@login_required()
def emergencyContactForm(request):
    print(request.method)

    match request.method:
        case 'GET':
            try:
                validPath = request.headers['HX-Current-URL'].split('/')[-2] == 'volunteer'
            except KeyError:
                return HttpResponseRedirect('/volunteer')
            if validPath:
                return render(request, 'volunteer/emergency-contacts.html', {'hx': check_if_hx(request)})
            else:
                return HttpResponseRedirect('/volunteer')
        case 'POST':
            data = request.POST
            create_emergency_contacts(request.user, data)
            request.method = 'GET' #Change the requst method so the next function renders instead of trying to parse the data
            return HTTPResponseHXRedirect('/volunteer')
        
@login_required()
def coreInfoForm(request):
    match request.method: #Handle request types
        case 'GET': #GET request
            try:
                validPath = request.headers['HX-Current-URL'].split('/')[-2] == 'volunteer' #Should only be coming from the initial URL view, swapped by HTMX
            except KeyError:
                return HttpResponseRedirect('/volunteer') #Redirect if incorrectly accessed
            if validPath:
                return render(request, 'volunteer/core-info.html', {'hx': check_if_hx(request)}) #Return form if correct
            else:
                return HttpResponseRedirect('/volunteer')  #Could be coming from HTMX but not from the correct URL
        case 'POST':
            data = request.POST
            print(data)
            createVolunteer(data, request.user)
            request.method = 'GET' #Change the requst method so the next function renders instead of trying to parse the data
            return (emergencyContactForm(request)) 
            #return HTTPResponseHXRedirect('/volunteer')  

def sign_up(request):
    if request.method == 'GET':
        return render(request, 'volunteer/sign_up.html', {'hx': check_if_hx(request)})
    elif request.method == 'POST':
        data = request.POST
        print(data)
        #create django user
        user = User.objects.create_user(data['email'], data['email'], data['password'])
        user.save()
        #create volunteer -> redirect to onboarding
        return HTTPResponseHXRedirect('/volunteer')

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/volunteer')