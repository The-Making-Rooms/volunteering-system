# Generated by Django 5.0 on 2024-02-08 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0005_location_city_location_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplimentaryInfoRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]