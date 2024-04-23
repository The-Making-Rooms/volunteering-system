# Generated by Django 5.0.2 on 2024-03-27 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0013_opportunityview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='second_line',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
