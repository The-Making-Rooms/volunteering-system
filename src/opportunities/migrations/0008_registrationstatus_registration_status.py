# Generated by Django 5.0.2 on 2024-03-16 09:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0007_supplimentaryinforequirement_info_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=200)),
                ('date', models.DateField()),
            ],
        ),
        migrations.AddField(
            model_name='registration',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='opportunities.registrationstatus'),
        ),
    ]
