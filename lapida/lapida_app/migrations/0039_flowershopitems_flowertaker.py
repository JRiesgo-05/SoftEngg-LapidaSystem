# Generated by Django 3.1.6 on 2022-03-30 10:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lapida_app', '0038_auto_20210619_0004'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlowerTaker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('flower_shops', models.CharField(choices=[('CF', 'Citfora Flowers'), ('GF', 'Gertudes Flowershop'), ('RG', "Raphael's Gifts"), ('LR', 'La Rose')], max_length=2)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FlowerShopItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flower_name', models.CharField(max_length=150)),
                ('price', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=150)),
                ('image', models.ImageField(blank=True, default='image/upload_default_flower.png', upload_to='image')),
                ('flower_taker', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lapida_app.flowertaker')),
            ],
        ),
    ]
