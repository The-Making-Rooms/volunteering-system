# Generated by Django 5.0.4 on 2024-05-13 16:46

import django.db.models.deletion
import opportunities.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0038_icon_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='benefit',
            name='icon',
            field=models.ForeignKey(default=opportunities.models.get_default_icon, on_delete=django.db.models.deletion.CASCADE, to='opportunities.icon'),
        ),
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]