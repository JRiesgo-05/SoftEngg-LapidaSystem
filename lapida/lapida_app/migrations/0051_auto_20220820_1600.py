# Generated by Django 3.1.6 on 2022-08-20 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lapida_app', '0050_order_user_prayer_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_user',
            name='floral_service',
            field=models.CharField(blank=True, max_length=1200),
        ),
        migrations.AlterField(
            model_name='order_user',
            name='gravesite_service',
            field=models.CharField(blank=True, max_length=1200),
        ),
        migrations.AlterField(
            model_name='order_user',
            name='prayer_service',
            field=models.CharField(blank=True, max_length=1200),
        ),
    ]
