# Generated by Django 5.0.2 on 2024-03-16 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0011_remove_volunteerregistrationstatus_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='opportunity',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='start_date',
        ),
    ]
