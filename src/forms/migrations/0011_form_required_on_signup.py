# Generated by Django 5.0.4 on 2024-08-26 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0010_alter_answer_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='required_on_signup',
            field=models.BooleanField(default=False),
        ),
    ]
