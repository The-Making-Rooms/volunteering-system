# Generated by Django 5.0.4 on 2024-09-04 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0017_alter_volunteer_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteeraddress',
            name='city',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='volunteeraddress',
            name='first_line',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]