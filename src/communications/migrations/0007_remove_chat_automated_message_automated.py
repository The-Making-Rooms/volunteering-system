# Generated by Django 5.0.4 on 2024-05-15 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communications', '0006_chat_automated_alter_automatedmessage_organisation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='automated',
        ),
        migrations.AddField(
            model_name='message',
            name='automated',
            field=models.BooleanField(default=False),
        ),
    ]
