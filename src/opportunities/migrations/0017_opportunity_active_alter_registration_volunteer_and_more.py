# Generated by Django 5.0.2 on 2024-03-28 13:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0016_remove_registration_user_and_more'),
        ('volunteer', '0008_alter_volunteer_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='opportunity',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='volunteer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='volunteer.volunteer'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='volunteerregistrationstatus',
            name='Registration',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='opportunities.registration'),
            preserve_default=False,
        ),
    ]
