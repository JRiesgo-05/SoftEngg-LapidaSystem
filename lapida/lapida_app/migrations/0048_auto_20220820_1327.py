# Generated by Django 3.1.6 on 2022-08-20 05:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lapida_app', '0047_auto_20220820_1311'),
    ]

    operations = [
        migrations.RenameField(
            model_name='flowertaker_task',
            old_name='caretaker',
            new_name='flowertaker',
        ),
    ]
