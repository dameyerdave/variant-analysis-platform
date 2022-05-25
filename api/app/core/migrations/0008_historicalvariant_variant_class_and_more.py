# Generated by Django 4.0.3 on 2022-05-24 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remove_historicalvariant_ensembl_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalvariant',
            name='variant_class',
            field=models.TextField(help_text='The class of the variant', null=True),
        ),
        migrations.AddField(
            model_name='variant',
            name='variant_class',
            field=models.TextField(help_text='The class of the variant', null=True),
        ),
    ]