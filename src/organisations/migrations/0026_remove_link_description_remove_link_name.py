# Generated by Django 5.0.4 on 2024-05-08 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0025_video_video_thumbnail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='link',
            name='description',
        ),
        migrations.RemoveField(
            model_name='link',
            name='name',
        ),
    ]
