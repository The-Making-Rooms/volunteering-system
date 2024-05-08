# Generated by Django 5.0.4 on 2024-05-06 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0026_remove_location_city_remove_location_description_and_more'),
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