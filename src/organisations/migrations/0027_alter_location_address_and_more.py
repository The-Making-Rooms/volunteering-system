# Generated by Django 5.0.6 on 2024-05-14 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0026_remove_link_description_remove_link_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='description',
            field=models.TextField(),
        ),
    ]
