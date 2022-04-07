# Generated by Django 4.0.3 on 2022-04-07 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_gene_options_alter_patient_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Phenotype',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('phenotype', models.TextField()),
                ('inheritance_mode', models.CharField(choices=[('AD', 'AD'), ('AR', 'AR'), ('DD', 'DD'), ('DRMD', 'DRMD'), ('MR', 'MR'), ('XD', 'XD'), ('XR', 'XR')], max_length=4)),
                ('gene', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.gene')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
