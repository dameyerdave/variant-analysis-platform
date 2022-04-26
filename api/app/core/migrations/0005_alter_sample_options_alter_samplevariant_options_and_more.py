# Generated by Django 4.0.3 on 2022-04-12 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_phenotype_options_alter_samplevariant_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sample',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='samplevariant',
            options={'ordering': ['sample__id']},
        ),
        migrations.RenameField(
            model_name='sample',
            old_name='sample_id',
            new_name='id',
        ),
        migrations.AlterField(
            model_name='phenotype',
            name='inheritance_mode',
            field=models.CharField(choices=[('AD', 'AD'), ('AR', 'AR'), ('DD', 'DD'), ('DR', 'DR'), ('MD', 'MD'), ('MR', 'MR'), ('XD', 'XD'), ('XR', 'XR')], max_length=2),
        ),
        migrations.AlterUniqueTogether(
            name='samplevariant',
            unique_together={('sample', 'variant')},
        ),
    ]