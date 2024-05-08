# Generated by Django 5.0.4 on 2024-05-06 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0019_alter_linktype_icon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='city',
        ),
        migrations.RemoveField(
            model_name='location',
            name='first_line',
        ),
        migrations.RemoveField(
            model_name='location',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='location',
            name='longitude',
        ),
        migrations.RemoveField(
            model_name='location',
            name='postcode',
        ),
        migrations.RemoveField(
            model_name='location',
            name='second_line',
        ),
        migrations.AddField(
            model_name='location',
            name='place_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]