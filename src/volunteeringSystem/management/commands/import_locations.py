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
                            location = OrganisationLocation()
                            location.organisation = organisation
                            location.name = row[0]
                            location.address = row[1]
                            location.postcode = row[2]
                            location.save()