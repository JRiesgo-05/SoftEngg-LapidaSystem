# Generated by Django 3.1.5 on 2021-03-05 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lapida_app', '0016_caretaker_caretaker_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_user',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('C', 'Cancelled'), ('C', 'Completed'), ('Pa', 'Paid'), ('O', 'Ongoing')], max_length=2),
        ),
    ]
