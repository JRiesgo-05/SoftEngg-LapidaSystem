# Generated by Django 3.1.5 on 2021-06-15 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lapida_app', '0035_auto_20210615_2153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
