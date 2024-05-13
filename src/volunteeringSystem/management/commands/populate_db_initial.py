"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
import logging

from django.core.management.base import BaseCommand
from opportunities.models import Icon, RegistrationStatus


class Command(BaseCommand):
    help = 'Creates volunteer statuses.'

    def handle(self, *args, **options):
        statuses = ['completed', 'awaiting_approval', 'stopped', 'paused', 'active']
        for status in statuses:
            RegistrationStatus.objects.get_or_create(status=status)
            self.stdout.write(self.style.SUCCESS(f'Successfully created {status} status'))
            
        
        
        