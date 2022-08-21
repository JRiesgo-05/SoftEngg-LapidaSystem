# Generated by Django 3.1.6 on 2022-08-20 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lapida_app', '0040_remove_order_user_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_user',
            name='flower_shop',
            field=models.CharField(choices=[('CF', 'Citfora Flowers'), ('GF', 'Gertudes Flowershop'), ('RG', "Raphael's Gifts"), ('LR', 'La Rose')], default='CF', max_length=2),
        ),
    ]