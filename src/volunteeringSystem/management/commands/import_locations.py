import logging

from django.core.management.base import BaseCommand
from organisations.models import Organisation, Location as OrganisationLocation
from opportunities.models import Location as OpportunityLocation, Opportunity
import os
from django.core.files import File
import csv
from recurrence import Recurrence

class Command(BaseCommand):
    help = 'Creates volunteer statuses.'
    
    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        import_path = options['path']
        
        files = os.listdir(import_path)
        
        import_count = 0
        
        for folder in files:
            
            #check if loop is a file
            if os.path.isfile(import_path + folder):
                continue
            
            folder_path = import_path + folder + '/'
            files = os.listdir(folder_path)
            
            if Organisation.objects.filter(name=folder).exists():
                if 'locations.csv' in files:
                    organisation = Organisation.objects.get(name=folder)
                    with open(folder_path + 'locations.csv') as file:
                        reader = csv.reader(file)
                        for row in reader:
                            #skip header
                            if row[0] == 'name':
                                continue
                            #name,address,place_id,longitude,latitude
                            if OrganisationLocation.objects.filter(place_id=row[2]).exists():
                                continue
                            location = OrganisationLocation()
                            location.organisation = organisation
                            location.name = row[0]
                            location.address = row[1]
                            location.place_id = row[2]
                            location.longitude = row[3]
                            location.latitude = row[4]
                if 'opportunity_locations.csv' in files:
                    with open(folder_path + 'opportunity_locations.csv') as file:
                        reader = csv.reader(file)
                        for row in reader:
                            #skip header
                            if row[0] == 'opportunity':
                                continue
                            #opportunity,name,address,place_id,longitude,latitude
                            print(row[0])
                            opportunity = Opportunity.objects.get(name=row[0])
                            if OpportunityLocation.objects.filter(opportunity=opportunity, place_id=row[3]).exists():
                                continue
                            location = OpportunityLocation()
                            location.opportunity = opportunity
                            location.name = row[1]
                            location.address = row[2]
                            location.place_id = row[3]
                            location.longitude = row[4]
                            location.latitude = row[5]
                            location.save()