# Generated by Django 5.0.4 on 2024-06-06 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0011_remove_mentorrecord_mentor_mentorrecord_organisation'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentorsession',
            name='session_notes',
            field=models.TextField(blank=True),
        ),
    ]
