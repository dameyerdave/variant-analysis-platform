# Generated by Django 4.0.3 on 2022-03-25 07:26

import django.core.validators
from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_transcript_hgvsg'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prename', models.CharField(max_length=50)),
                ('middle_name', models.CharField(max_length=50)),
                ('surename', models.CharField(max_length=50)),
                ('street', models.CharField(max_length=50)),
                ('house_number', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('zip', models.IntegerField(validators=[django.core.validators.MinValueValidator(1000)])),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('sample_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('variants', models.ManyToManyField(related_name='samples', to='core.variant')),
            ],
        ),
    ]
