# Generated by Django 4.2.1 on 2023-06-07 10:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('greatkartapp', '0023_alter_order_address_line_2_alter_order_phone_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='color',
        ),
        migrations.RemoveField(
            model_name='orderproduct',
            name='size',
        ),
    ]
