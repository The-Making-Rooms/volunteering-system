# Generated by Django 5.0.4 on 2024-05-06 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0021_rename_description_location_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
