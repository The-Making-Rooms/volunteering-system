# Generated by Django 5.0.4 on 2024-05-07 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0024_alter_thematiccategory_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='video_thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='videos/'),
        ),
    ]