# Generated by Django 5.0.4 on 2024-06-06 10:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0028_badge_badgeopporunity_volunteerbadge'),
        ('volunteer', '0010_mentorrecord_mentornotes_mentorsession'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mentorrecord',
            name='mentor',
        ),
        migrations.AddField(
            model_name='mentorrecord',
            name='organisation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='organisations.organisation'),
            preserve_default=False,
        ),
    ]
