# Generated by Django 5.0 on 2023-12-13 17:56

import djrichtextfield.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0002_rename_registrations_registration_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='benefit',
            name='name',
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='description',
            field=djrichtextfield.models.RichTextField(),
        ),
    ]
