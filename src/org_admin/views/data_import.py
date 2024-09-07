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
from forms.models import Form, Question, Response, Answer, Options

def data_import(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')
        
    if request.method == 'POST':
        try:
            csv_file = request.FILES['csv_file']
            
            # Read the CSV file in memory
            data_set = csv_file.read().decode()
            io_string = io.StringIO(data_set)
            csv_reader = csv.DictReader(io_string, delimiter=',', quotechar='"')
            
            dicts = []
            errors = []
            num = 0
            
            for row in csv_reader:
                try:
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
                        last_name=' '.join(row['Full Name:'].split(' ')[1:]),
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
                            elif interest == 'Blackburn Library Service':
                                interest = 'Blackburn with Darwen Library Service'
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
                                
                    try:            
                        create_survey_response(row, user)
                    except Exception as e:
                        return HttpResponse('An error occurred while creating survey response {}'.format(e))
                    
                    num += 1
                except Exception as e:
                    errors.append(row)
                    print(e)
                        
            return HttpResponse('{} Data imported successfully {}'.format(num, errors))
        except Exception as e:
            print(e)
            return HttpResponse('An error occurred while importing the data {}'.format(e))
                    
    return render(request, 'org_admin/data_import.html')


def create_survey_response(data, user):
    try:
        form = Form.objects.get(required_on_signup=True)
        form_questions = Question.objects.filter(form=form)
        
        errors = []
        string_date = data['Date:']
        
        response = Response(
            user=user,
            form=form,
            response_date=datetime.datetime.strptime(string_date, '%d/%m/%Y') if len(string_date) > 0 else datetime.datetime.now()
        ) if not Response.objects.filter(user=user, form=form).exists() else Response.objects.get(user=user, form=form)
        
        response.save()
        print('Error creating survey response: Catch A')
        for question in form_questions:
            print('Error creating survey response: Catch B')
            if question.question_type == "text":
                #fuzzy find a key in data that matches the question
                fuzzy_key = fuzzy_return_closest_key(question.question, data.keys())
                if fuzzy_key:
                    answer = Answer(
                        question=question,
                        answer=data[fuzzy_key],
                        response=response
                    ) if not Answer.objects.filter(question=question, response=response).exists() else Answer.objects.get(question=question, response=response)
                    answer.save()
                    print('Error creating survey response: Catch c')
                else:
                    errors.append('Could not find a match for question: ' + question.question)
            elif question.question_type == "multi_choice":
                fuzzy_key = fuzzy_return_closest_key(question.question, data.keys())
                
                if fuzzy_key is None:
                    errors.append('Could not find a match for question: ' + question.question)
                    continue
                
                if '|' in data[fuzzy_key]:
                    answers = data[fuzzy_key].split('|')
                else:
                    answers = [data[fuzzy_key]]
                
                option_ids = []
                
                if question.question == 'Gender':
                    for answer in answers:
                        if answer.lower() == "male":
                            option_id = Options.objects.get(option='Male', question=question)
                            option_ids.append(str(option_id.id))
                        elif answer.lower() == "female":
                            option_id = Options.objects.get(option='Female', question=question)
                            option_ids.append(str(option_id.id))
                        else:
                            option_id = Options.objects.get(option='Other', question=question)
                            option_ids.append(str(option_id.id))
                            self_desc_ques = Question.objects.get(question='Gender - Prefer to self-describe', form=form)
                            ans = Answer(
                                question=self_desc_ques,
                                answer=answer,
                                response=response
                            ) if not Answer.objects.filter(question=self_desc_ques, response=response).exists() else Answer.objects.get(question=self_desc_ques, response=response)
                            ans.save()
                else:
                    for answer in answers:
                        option_id = fuzzy_return_closest_option(question, answer)
                        if option_id:
                            option_ids.append(str(option_id.id))
                        else:
                            if question.question == 'Ethnic Origin':
                                self_desc_ques = Question.objects.get(question="Ethinic Background - Other")
                                ans = Answer(
                                    question=self_desc_ques,
                                    answer=answer,
                                    response=response
                                ) if not Answer.objects.filter(question=self_desc_ques, response=response).exists() else Answer.objects.get(question=self_desc_ques, response=response)
                                ans.save()
                            else:
                                errors.append('{} Could not find a match for option- '.format(question.question) + answer)
                
                if len(option_ids) > 0:
                    answer = Answer(
                        question=question,
                        answer=','.join(option_ids),
                        response=response
                    ) if not Answer.objects.filter(question=question, response=response).exists() else Answer.objects.get(question=question, response=response)
                    answer.save()
                    print('Error creating survey response: Catch c')
            elif question.question_type == "boolean":
                fuzzy_key = fuzzy_return_closest_key(question.question, data.keys())
                if data[fuzzy_key].lower() == 'yes':
                    answer = Answer(
                        question=question,
                        answer='yes',
                        response=response
                    ) if not Answer.objects.filter(question=question, response=response).exists() else Answer.objects.get(question=question, response=response)
                    answer.save()
                    print('Error creating survey response: Catch c')
                elif data[fuzzy_key].lower() == 'no':
                    answer = Answer(
                        question=question,
                        answer='no',
                        response=response
                    ) if not Answer.objects.filter(question=question, response=response).exists() else Answer.objects.get(question=question, response=response)
                    answer.save()
                    print('Error creating survey response: Catch c')
                else:
                    errors.append('Could not find a match for boolean question: ' + question.question)
                    
        print(errors)
    except Exception as e:
        print("Error creating survey response: ", e)
        
                
                
def utils_fix_organisation_interests(request):
    interest_question = Question.objects.get(question="Organisations of Interest")
    responses = Response.objects.filter(form=interest_question.form)
    errors = []
    count = 0
    
    try:
    
        for response in responses:
            volunteer = Volunteer.objects.get(user=response.user)
            
            try:
                answer = Answer.objects.get(question=interest_question, response=response)
            except:
                errors.append('Could not find answer for response: ' + str(response.id))
                continue
            
            orgs = answer.answer.split(",")
            org_ids = [Options.objects.get(id=org) for org in orgs]
            
            for org_id in org_ids:
                interest = org_id.option
                if interest == 'Blackburn Youth Zone':
                    interest = 'Blackburn & Darwen Youth Zone'
                elif interest == 'Blackburn Library Service':
                    interest = 'Blackburn with Darwen Library Service'
                elif interest == 'Festivals (Festival of light, National Festival of Making, British Textile Biennial)':
                    festival_orgs = ['Festival of Light', 'National Festival of Making', 'British Textile Biennial']
                    for festival in festival_orgs:
                        org = fuzzy_return_org(festival)
                        if org:
                            create_follower_if_not_exists(volunteer, org)
                            count += 1
                        else:
                            errors.append('Could not find organisation: ' + festival)

                
                org = fuzzy_return_org(org_id.option)
                if org:
                    create_follower_if_not_exists(volunteer, org)
                    count += 1
                else:
                    errors.append('Could not find organisation: ' + org_id.option)
                    
    except Exception as e:
        print(e)
        return HttpResponse('An error occurred while fixing organisation interests {}'.format(e))

    return HttpResponse('{} Organisation interests fixed successfully {}'.format(count, errors))

def create_follower_if_not_exists(volunteer, org):
    if not OrganisationInterest.objects.filter(volunteer=volunteer, organisation=org).exists():
        org_interest = OrganisationInterest(
            volunteer=volunteer,
            organisation=org
        )
        org_interest.save()

def fuzzy_return_closest_option(question, option):
    options = Options.objects.filter(question=question)
    option_names = [option.option for option in options]
    
    best_match, score = process.extractOne(option, option_names, scorer=fuzz.partial_ratio)
    
    print("{}: Best match for key:{} system:{}, {}".format(question.question, option, best_match, score))
    
    if score >= 80:
        return Options.objects.get(option=best_match, question=question)
    
    return None


def fuzzy_return_closest_key(string, keys):
    ratios = [{'key': key, 'ratio': fuzz.ratio(string, key)} for key in keys]
    
    #print highest ratio
    print("best ratio for sting {} is {}. Key:{}".format(string, max(ratios, key=lambda x:x['ratio'])['ratio'], max(ratios, key=lambda x:x['ratio'])['key']))
    
    #return highest match if it is above 80
    if max(ratios, key=lambda x:x['ratio'])['ratio'] >= 80:
        return max(ratios, key=lambda x:x['ratio'])['key']
    return None

def fuzzy_return_org(org_name):
    orgs = Organisation.objects.all()
    org_names = [org.name for org in orgs]
    
    # Use fuzzy matching to find the best match
    best_match, score = process.extractOne(org_name, org_names, scorer=fuzz.partial_ratio)
    
    if score >= 80:  # You can adjust the threshold as needed
        return Organisation.objects.get(name=best_match)
    return None