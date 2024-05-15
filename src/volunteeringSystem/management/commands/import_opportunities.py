import logging

from django.core.management.base import BaseCommand
from organisations.models import Organisation
from opportunities.models import Opportunity, Benefit, Icon, Image, Video, Tag, LinkedTags, Location
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
                
                if 'opportunities.csv' in files:
                    organisation = Organisation.objects.get(name=folder)
                    #name,description,start_time,end_time,recurrences,featured,benefits,benefit_icons
                    with open(folder_path + 'opportunities.csv') as file:
                        reader = csv.reader(file)
                        for row in reader:
                            #skip header
                            if row[0] == 'name':
                                continue
                            print ("start: {} end: {}".format(row[2], row[3]))
                            opportunity = Opportunity()
                            opportunity.organisation = organisation
                            opportunity.name = row[0]
                            opportunity.description = row[1]
                            opportunity.start_time = row[2] if row[2] != '' else None
                            opportunity.end_time = row[3] if row[3] != '' else None
                            opportunity.recurrences = Recurrence()
                            opportunity.featured = row[5]
                            opportunity.save()
                            
                            #remove spaces, brackets and quotes from string and split by comma
                            
                            #format is ['this is a test', 'benefit2', 'benefit3']
                            benefits = row[6].replace('[\'' , '').replace('\']', '').replace('\', \'', ',l').split(',l')
                            #format is ['icon1.png', 'icon2.png', 'icon3.png']
                            benefit_icons = row[7].replace('[\'' , '').replace('\']', '').replace('\', \'', ',l').split(',l')
                            
                            tags = row[8].replace('[\'' , '').replace('\']', '').replace('\', \'', ',l').split(',l')
                            
                            for tag in tags:
                                if tag == '':
                                    continue
                                tag, returnv = Tag.objects.get_or_create(tag=tag)
                                linked_tag = LinkedTags()
                                linked_tag.tag = tag
                                linked_tag.opportunity = opportunity
                                linked_tag.save()
                                
                            
                            for index, r_benefit in enumerate(benefits):
                                print("beneft: {}".format(r_benefit))
                                if r_benefit == '' or r_benefit == '[]':
                                    continue
                                
                                benefit = Benefit()
                                benefit.opportunity = opportunity
                                benefit.description = r_benefit
                                
                                try:
                                    icon = Icon.objects.get(name=benefit_icons[index].split('.')[0])
                                    benefit.icon = icon
                                except:
                                    print(f'Icon not found')
                                    icon = Icon.objects.get(name='default_icon')
                                    benefit.icon = icon
                                
                                benefit.save()
                                
                        import_count += 1
                        print(f'Imported {import_count} opportunities')
                
                    if 'opportunity_media.csv' in files:
                        with open(folder_path + 'opportunity_media.csv') as file:
                            reader = csv.reader(file)
                            for row in reader:
                                if row[0] == 'opportunity_name':
                                    continue
                                if row[1] == 'image':
                                    image = Image()
                                    image.image = File(open(folder_path+ 'media/' + row[2], 'rb'), name=row[2])
                                    image.thumbnail_image = File(open(folder_path+ 'media_thumbnail/' + row[3], 'rb'), name=row[3])
                                    image.opportunity = Opportunity.objects.get(name=row[0])
                                    image.save()
                                elif row[1] == 'video':
                                    video = Video()
                                    video.video = File(open(folder_path+ 'media/' + row[2], 'rb'), name=row[2])
                                    video.video_thumbnail = File(open(folder_path+ 'media_thumbnail/' + row[3], 'rb'), name=row[3])
                                    video.opportunity = Opportunity.objects.get(name=row[0])
                                    video.save()
            else:
                continue
            
            
        