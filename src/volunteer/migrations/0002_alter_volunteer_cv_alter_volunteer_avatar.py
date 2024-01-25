# Generated by Django 5.0 on 2023-12-27 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteer',
            name='CV',
            field=models.FileField(blank=True, upload_to='CV/'),
        ),
        migrations.AlterField(
            model_name='volunteer',
            name='avatar',
            field=models.ImageField(blank=True, upload_to='avatars/'),
        ),
    ]
