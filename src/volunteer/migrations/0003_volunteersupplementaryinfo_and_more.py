# Generated by Django 5.0 on 2024-02-08 16:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0002_supplementaryinfo_supplementaryinfograntee'),
    ]

    operations = [
        migrations.CreateModel(
            name='VolunteerSupplementaryInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated', models.DateField()),
                ('data', models.CharField(max_length=200)),
                ('info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='volunteer.supplementaryinfo')),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='volunteer.volunteer')),
            ],
        ),
        migrations.AlterField(
            model_name='supplementaryinfograntee',
            name='info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='volunteer.volunteersupplementaryinfo'),
        ),
    ]
