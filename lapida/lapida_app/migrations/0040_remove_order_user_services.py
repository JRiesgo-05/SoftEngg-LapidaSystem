# Generated by Django 3.1.6 on 2022-08-20 03:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lapida_app', '0039_flowershopitems_flowertaker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order_user',
            name='services',
        ),
    ]