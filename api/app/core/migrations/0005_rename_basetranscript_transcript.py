# Generated by Django 4.0.3 on 2022-03-09 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rename_alt_variant_allele_string_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BaseTranscript',
            new_name='Transcript',
        ),
    ]
