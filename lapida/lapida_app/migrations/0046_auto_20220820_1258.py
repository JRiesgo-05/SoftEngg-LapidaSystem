# Generated by Django 3.1.6 on 2022-08-20 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lapida_app', '0045_auto_20220820_1244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_user',
            name='floral_status',
            field=models.CharField(choices=[('P', 'Pending'), ('Ca', 'Cancelled'), ('C', 'Completed'), ('Pa', 'Paid'), ('O', 'Ongoing'), ('NT', 'Not taken'), ('NA', 'Did Not Avail')], default='NA', max_length=2),
        ),
        migrations.AlterField(
            model_name='order_user',
            name='gravesite_status',
            field=models.CharField(choices=[('P', 'Pending'), ('Ca', 'Cancelled'), ('C', 'Completed'), ('Pa', 'Paid'), ('O', 'Ongoing'), ('NT', 'Not taken'), ('NA', 'Did Not Avail')], default='NA', max_length=2),
        ),
    ]