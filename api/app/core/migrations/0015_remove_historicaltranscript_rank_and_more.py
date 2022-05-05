# Generated by Django 4.0.3 on 2022-05-05 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_remove_historicaltranscript_variant_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicaltranscript',
            name='rank',
        ),
        migrations.RemoveField(
            model_name='transcript',
            name='rank',
        ),
        migrations.CreateModel(
            name='VariantTranscript',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.PositiveIntegerField(default=0)),
                ('transcript', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_transcripts', to='core.transcript')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_transcripts', to='core.variant')),
            ],
        ),
    ]
