# Generated by Django 5.1.7 on 2025-04-06 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0018_alter_volunteeraddress_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteer',
            name='preferred_name',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
