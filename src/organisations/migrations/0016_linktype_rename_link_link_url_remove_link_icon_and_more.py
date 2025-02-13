# Generated by Django 5.0.2 on 2024-03-20 10:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0015_alter_location_latitude_alter_location_longitude'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.ImageField(blank=True, null=True, upload_to='')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.RenameField(
            model_name='link',
            old_name='link',
            new_name='url',
        ),
        migrations.RemoveField(
            model_name='link',
            name='icon',
        ),
        migrations.AddField(
            model_name='link',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organisations.linktype'),
        ),
    ]
