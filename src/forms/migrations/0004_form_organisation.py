# Generated by Django 5.0.4 on 2024-05-08 11:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0003_question_required_response_answer_response'),
        ('organisations', '0025_video_video_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='organisation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='organisations.organisation'),
            preserve_default=False,
        ),
    ]