import logging

from django.core.management.base import BaseCommand
from organisations.models import Organisation, Image, Video
import os
from django.core.files import File
import csv

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
            #check if organisation.csv exists
            if 'organisation.csv' in files:
                organisation = Organisation()
                with open(folder_path + 'organisation.csv') as file:
                    reader = csv.reader(file)
                    if not Organisation.objects.filter(name=folder).exists():   
                        for row in reader:
                            organisation.name = row[0]
                            organisation.description = row[1]
                            organisation.featured = True
                            organisation.save()
                        import_count += 1
                #check for any filenames ending in .png
                for file in files:
                    if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg'):
                        organisation.logo = File(open(folder_path + file, 'rb'), name=file)
                        organisation.save()
            
            if 'media.csv' in files:
                with open(folder_path + 'media.csv') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if row[0] == 'image':
                            image = Image()
                            image.image = File(open(folder_path+ '/media/' + row[1], 'rb'), name=row[1])
                            image.thumbnail_image = File(open(folder_path+ '/media_thumbnail/' + row[2], 'rb'), name=row[2])
                            image.organisation = organisation
                            image.save()
                        elif row[0] == 'video':
                            video = Video()
                            video.video = File(open(folder_path+ '/media/' + row[1], 'rb'), name=row[1])
                            video.video_thumbnail = File(open(folder_path+ '/media_thumbnail/' + row[2], 'rb'), name=row[2])
                            video.organisation = organisation
                            video.save()
            
            print ('Imported ' + str(import_count) + ' organisations')