# Generated by Django 5.0 on 2024-02-16 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0013_alter_location_second_line'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='longitude',
            field=models.FloatField(null=True),
        ),
    ]
