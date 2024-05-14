import logging

from django.core.management.base import BaseCommand
from opportunities.models import Icon
import os
from django.core.files import File

class Command(BaseCommand):
    help = 'Creates volunteer statuses.'
    
    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        import_path = options['path']
        
        files = os.listdir(import_path)
        
        for file in files:
            if file.endswith('.png'):
                print(file)
                icon = Icon()
                icon.name = file.split('.')[0]
                icon.icon = File(open(import_path + file, 'rb'), name=file)
                icon.save()
        