# Generated by Django 4.2.1 on 2023-12-08 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Links',
            new_name='Link',
        ),
        migrations.RenameModel(
            old_name='Videos',
            new_name='Video',
        ),
    ]
