# Generated by Django 5.1.7 on 2025-03-24 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org_admin', '0005_emaildraft_email_target_recipients'),
    ]

    operations = [
        migrations.AddField(
            model_name='emaildraft',
            name='send_confirmation_id',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='emaildraft',
            name='email_target_recipients',
            field=models.CharField(choices=[('organisations', 'Organisations'), ('volunteers', 'Volunteers'), ('all', 'All users')], max_length=20),
        ),
    ]
