# Generated by Django 5.0.4 on 2024-05-10 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0034_alter_tag_hex_colour'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='hex_colour_to',
            field=models.CharField(default='#000000', max_length=7),
        ),
    ]
