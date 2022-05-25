# Generated by Django 4.0.3 on 2022-05-24 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_historicalevidence'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalvariant',
            name='ensembl_id',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='historicalvariant',
            name='vrs_id',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='variant',
            name='ensembl_id',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='variant',
            name='vrs_id',
            field=models.TextField(null=True),
        ),
    ]