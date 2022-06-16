# Generated by Django 4.0.3 on 2022-06-10 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_variantconsequence_consequence_ranking'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsamplevariant',
            name='causative',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='samplevariant',
            name='causative',
            field=models.BooleanField(default=False),
        ),
    ]