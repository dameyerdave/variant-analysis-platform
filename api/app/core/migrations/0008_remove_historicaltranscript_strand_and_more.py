# Generated by Django 4.0.3 on 2022-04-26 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_patient_options_alter_phenotype_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicaltranscript',
            name='strand',
        ),
        migrations.RemoveField(
            model_name='transcript',
            name='strand',
        ),
    ]
