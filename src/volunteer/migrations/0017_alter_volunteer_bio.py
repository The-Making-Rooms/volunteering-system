# Generated by Django 5.0.6 on 2024-08-28 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0016_rename_mentorrecord_mentorsession_mentor_record'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteer',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
    ]


# Generated by Django 5.0.4 on 2024-09-04 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0016_rename_mentorrecord_mentorsession_mentor_record'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteer',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
    ]
