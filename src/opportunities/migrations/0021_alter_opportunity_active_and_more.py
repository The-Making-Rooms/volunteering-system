# Generated by Django 5.0.2 on 2024-04-02 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0020_opportunity_end_time_opportunity_start_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opportunity',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='registrationabsence',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
