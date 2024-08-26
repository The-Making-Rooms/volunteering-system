# Generated by Django 5.0.4 on 2024-08-26 09:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0011_form_required_on_signup'),
        ('organisations', '0029_alter_image_image_alter_image_thumbnail_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='form',
            name='organisation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organisations.organisation'),
        ),
    ]