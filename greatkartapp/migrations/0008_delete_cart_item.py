# Generated by Django 4.2.1 on 2023-05-26 13:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('greatkartapp', '0007_rename_cat_item_cart_item'),
    ]

    operations = [
        migrations.DeleteModel(
            name='cart_item',
        ),
    ]