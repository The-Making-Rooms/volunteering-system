# Generated by Django 5.0 on 2023-12-13 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0004_alter_image_image_alter_link_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='images/'),
        ),
    ]
