# Generated by Django 4.2.1 on 2023-06-09 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('greatkartapp', '0030_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='district',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='postal_code',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='street',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
