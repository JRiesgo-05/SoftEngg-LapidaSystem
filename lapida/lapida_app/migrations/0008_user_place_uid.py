# Generated by Django 3.1.5 on 2021-03-02 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lapida_app', '0007_auto_20210302_2049'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_place',
            name='uid',
            field=models.ForeignKey(default='hIP1ToECJxcUfazI', on_delete=django.db.models.deletion.CASCADE, to='lapida_app.masterdata'),
        ),
    ]
