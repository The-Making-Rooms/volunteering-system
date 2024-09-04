from django.contrib.auth.models import User
from volunteer.models import Volunteer, VolunteerAddress, VolunteerConditions
from organisations.models import Organisation, OrganisationInterest
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
import io
import random
import datetime

def data_import(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')
        
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        
        # Read the CSV file in memory
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        csv_reader = csv.DictReader(io_string, delimiter=',', quotechar='"')
        
        dicts = []
        errors = []
        
        for row in csv_reader:
            dicts.append(row)
            print(
                row['Full Name:'],
                row['Date of Birth:'],
                row['Postcode:'],
                row['Phone Number:'],
                row['Email Address:'],
                row['If yes, please give brief details of your disability'],
                row['Organisations of Interest:']
            )
            
            #check all rows are longer than 0 except for the disability row
            if len(row['Full Name:']) == 0 or len(row['Date of Birth:']) == 0 or len(row['Postcode:']) == 0 or len(row['Phone Number:']) == 0 or len(row['Email Address:']) == 0:
                errors.append(row)
                continue
            
            if row['Full Name:'] == '[RESTRICTED]':
                errors.append(row)
                continue
            
            
            
            # Check if the user already exists
            user, created = User.objects.get_or_create(
                username=row['Email Address:'],
                first_name=row['Full Name:'].split(' ')[0],
                last_name=''.join(row['Full Name:'].split(' ')[1:]),
                defaults={
                    'email': row['Email Address:'],
                    'password': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=12))
                }
            )
            
            if created:
                # User was created, set the password
                user.set_password(''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=12)))
                user.save()
            
            # Check if the volunteer already exists
            if not Volunteer.objects.filter(user=user).exists():
                volunteer = Volunteer(
                    user=user,
                    
                    date_of_birth=datetime.datetime.strptime(row['Date of Birth:'], '%d/%m/%Y'),
                    phone_number=row['Phone Number:'],
                )
                volunteer.save()
            else:
                volunteer = Volunteer.objects.get(user=user)
            
            if row['Postcode:']:
                # Check if the volunteer address already exists
                if not VolunteerAddress.objects.filter(volunteer=volunteer, postcode=row['Postcode:']).exists():
                    address = VolunteerAddress(
                        volunteer=volunteer,
                        postcode=row['Postcode:'],
                        # Add other address fields here if necessary
                    )
                    address.save()
                    
            if len(row['If yes, please give brief details of your disability']) > 0:
                if not VolunteerConditions.objects.filter(volunteer=volunteer, disclosures=row['If yes, please give brief details of your disability']).exists():
                    condition = VolunteerConditions(
                        volunteer=volunteer,
                        disclosures=row['If yes, please give brief details of your disability']
                    )
                    condition.save()
                    
            if len(row['Organisations of Interest:']) > 0:
                if '|' in row['Organisations of Interest:']:
                    interests = row['Organisations of Interest:'].split('|')
                else:
                    interests = [row['Organisations of Interest:']]
                    
                for interest in interests:
                    if interest == 'Blackburn Youth Zone':
                        interest = 'Blackburn & Darwen Youth Zone'
                    org = fuzzy_return_org(interest)
                    if org:
                        if not OrganisationInterest.objects.filter(volunteer=volunteer, organisation=org).exists():
                            org_interest = OrganisationInterest(
                                volunteer=volunteer,
                                organisation=org
                            )
                            org_interest.save()
                    else:
                        errors.append('Could not find organisation: ' + interest)
                        
                    
                
                
                    
        return HttpResponse('Data imported successfully {}'.format(errors))
                    
    return render(request, 'org_admin/data_import.html')


def fuzzy_return_org(org_name):
    orgs = Organisation.objects.all()
    org_names = [org.name for org in orgs]
    
    # Use fuzzy matching to find the best match
    best_match, score = process.extractOne(org_name, org_names, scorer=fuzz.partial_ratio)
    
    if score >= 80:  # You can adjust the threshold as needed
        return Organisation.objects.get(name=best_match)
    return None