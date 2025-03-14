# Generated by Django 5.0 on 2024-01-24 14:28

import djrichtextfield.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0004_tag_linkedtags'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='city',
            field=models.CharField(default='Blackburn', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='description',
            field=djrichtextfield.models.RichTextField(default='N/A'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='first_line',
            field=models.CharField(default='N/A', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='postcode',
            field=models.CharField(default='N/A', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='second_line',
            field=models.CharField(default='N/A', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='opportunity',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]
