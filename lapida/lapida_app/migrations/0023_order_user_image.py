# Generated by Django 3.1.5 on 2021-03-07 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lapida_app', '0022_auto_20210306_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_user',
            name='image',
            field=models.ImageField(blank=True, default='image/upload_default.png', upload_to='image'),
        ),
    ]
