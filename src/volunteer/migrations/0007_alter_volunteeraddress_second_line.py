# Generated by Django 5.0.2 on 2024-03-26 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0006_alter_volunteer_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteeraddress',
            name='second_line',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
