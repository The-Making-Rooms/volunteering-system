# Generated by Django 5.0.4 on 2024-08-26 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0015_alter_mentornotes_created_by'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mentorsession',
            old_name='MentorRecord',
            new_name='mentor_record',
        ),
    ]
