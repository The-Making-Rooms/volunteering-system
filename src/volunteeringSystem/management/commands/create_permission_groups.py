"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

GROUPS = ['organisation']
MODELS = ['organisation', 'opportunity', 'registration', 'volunteer']
PERMISSIONS = ['view', ]  # For now only view permission by default for all, others include add, delete, change

class Command(BaseCommand):
    help = 'Creates read only default permission groups for users'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='organisation')
        print(group)
        # Create permissions
        for model in MODELS:
            for permission in PERMISSIONS:
                codename = f'{permission}_{model}'
                name = f'Can {permission} {model}'
                permission_to_add = Permission.objects.get(codename=codename)
                group.permissions.add(permission_to_add)
        
        print('Permission groups created successfully')
        