# Generated by Django 5.1.7 on 2025-04-05 14:24

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0017_formresponserequirement_assigned_and_more'),
        ('opportunities', '0046_alter_benefit_opportunity'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SuperForm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=500)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='superforms/')),
                ('submitted_message', models.TextField(blank=True, null=True)),
                ('background_colour', models.CharField(default='#FFFFFF', max_length=7)),
                ('card_background_colour', models.CharField(default='#FFFFFF', max_length=7)),
                ('card_text_colour', models.CharField(default='#000000', max_length=7)),
                ('show_form_titles', models.BooleanField(default=True)),
                ('show_form_descriptions', models.BooleanField(default=True)),
                ('forms_to_complete', models.ManyToManyField(blank=True, to='forms.form')),
                ('opportunity_to_register', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='opportunities.opportunity')),
            ],
        ),
        migrations.CreateModel(
            name='SuperFormRegistration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('submitted', models.DateTimeField(auto_now_add=True)),
                ('superform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forms.superform')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
