# Generated by Django 5.0 on 2024-02-09 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0012_alter_location_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='second_line',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]