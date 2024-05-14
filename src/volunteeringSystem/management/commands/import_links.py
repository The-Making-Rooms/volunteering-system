import logging

from django.core.management.base import BaseCommand
from organisations.models import Organisation, Link, LinkType
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
        
        if 'link_types.csv' in files:
                print("found_link_types")
                with open(import_path + 'link_types.csv') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        print(row)
                        if row[0] == 'name':
                            continue
                        if not LinkType.objects.filter(name=row[0]).exists():
                            link_type = LinkType()
                            link_type.name = row[0]
                            link_type.icon = File(open(import_path + 'links/' + row[1], 'rb'), name=row[1])
                            link_type.save()
        
        for folder in files:

            #check if loop is a file
            if os.path.isfile(import_path + folder):
                continue
            
            folder_path = import_path + folder + '/'
            files = os.listdir(folder_path)
            
            if Organisation.objects.filter(name=folder).exists():
                if 'links.csv' in files:
                    org = Organisation.objects.get(name=folder)
                    with open(folder_path + 'links.csv') as file:
                        reader = csv.reader(file)
                        for row in reader:
                            print(row)
                            if row[0] == 'url':
                                continue
                            org_link = Link()
                            org_link.organisation = org
                            org_link.url = row[0]
                            print(row[1])
                            org_link.link_type = LinkType.objects.get(name=row[1])
                            try:
                                org_link.save()
                            except:
                                print("failed to save link")
                                print(org_link.url)
                                print(org_link.link_type)
                                print(org_link.organisation)
                                print("end")