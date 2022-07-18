# Generated by Django 4.0.3 on 2022-07-18 11:51

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Disease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('identifier', models.CharField(max_length=8, unique=True)),
                ('name', models.TextField()),
                ('type', models.CharField(choices=[('disease', 'disease'), ('phenotype', 'phenotype'), ('group', 'group')], default=None, max_length=9)),
                ('semantic_type', models.CharField(max_length=50, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DiseaseClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=20, unique=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='DiseaseDiseaseClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='DiseaseEvidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('reference', models.TextField()),
                ('source', models.CharField(choices=[('Unknown', 'Unknown'), ('Pubmed', 'Pubmed'), ('GoogleScholar', 'GoogleScholar'), ('Internet', 'Internet'), ('Internal', 'Internal')], default='Unknown', max_length=13)),
                ('title', models.TextField()),
                ('summary', models.TextField()),
                ('evidence_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('symbol', models.CharField(max_length=20, unique=True)),
                ('ensembl_id', models.CharField(max_length=15, null=True)),
                ('entrez_id', models.IntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalDisease',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('identifier', models.CharField(db_index=True, max_length=8)),
                ('name', models.TextField()),
                ('type', models.CharField(choices=[('disease', 'disease'), ('phenotype', 'phenotype'), ('group', 'group')], default=None, max_length=9)),
                ('semantic_type', models.CharField(max_length=50, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical disease',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalDiseaseEvidence',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical disease evidence',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalEvidence',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('reference', models.TextField()),
                ('source', models.CharField(choices=[('Unknown', 'Unknown'), ('Pubmed', 'Pubmed'), ('GoogleScholar', 'GoogleScholar'), ('Internet', 'Internet'), ('Internal', 'Internal')], default='Unknown', max_length=13)),
                ('title', models.TextField()),
                ('summary', models.TextField()),
                ('evidence_date', models.DateTimeField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical evidence',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalGene',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('symbol', models.CharField(db_index=True, max_length=20)),
                ('ensembl_id', models.CharField(max_length=15, null=True)),
                ('entrez_id', models.IntegerField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical gene',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPatient',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('prename', models.CharField(max_length=50)),
                ('middle_name', models.CharField(max_length=50)),
                ('surename', models.CharField(max_length=50)),
                ('street', models.CharField(max_length=50)),
                ('house_number', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('zip', models.IntegerField(validators=[django.core.validators.MinValueValidator(1000)])),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('email', models.EmailField(max_length=254)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical patient',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPhenotype',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('phenotype', models.TextField()),
                ('inheritance_modes', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), null=True, size=None)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical phenotype',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalSample',
            fields=[
                ('id', models.CharField(db_index=True, max_length=20)),
                ('tissue', models.CharField(choices=[('unknown', 'unknown'), ('blood', 'blood'), ('hair', 'hair'), ('skin', 'skin'), ('amniotic fluid', 'amniotic fluid'), ('inside surface of the cheek', 'inside surface of the cheek')], default='unknown', max_length=27)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical sample',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalSampleVariant',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('zygosity', models.CharField(choices=[('Homozygous', 'Homozygous'), ('Heterozygous', 'Heterozygous'), ('Hemizygous', 'Hemizygous'), ('Homoplasmic', 'Homoplasmic'), ('Heteroplasmic', 'Heteroplasmic'), ('Zero_coverage_region', 'Zero_coverage_region')], default=None, max_length=20, null=True)),
                ('causative', models.BooleanField(default=False, help_text='If true This is a causative variant in this sample')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical sample variant',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalTranscript',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('ensembl_id', models.TextField(null=True)),
                ('refseq_id', models.TextField(null=True)),
                ('name', models.TextField()),
                ('hgvsg', models.TextField(null=True)),
                ('hgvsc', models.TextField(null=True)),
                ('hgvsp', models.TextField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical transcript',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalTranscriptEvidence',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical transcript evidence',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalVariant',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('vrs_id', models.TextField(null=True)),
                ('assembly', models.CharField(choices=[('GRCh38', 'GRCh38'), ('GRCh37', 'GRCh37')], max_length=6)),
                ('chromosome', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('X', 'X'), ('Y', 'Y')], max_length=2)),
                ('start', models.IntegerField(help_text='The start of the variant')),
                ('end', models.IntegerField(help_text='The end of the variant')),
                ('allele_string', models.TextField()),
                ('variant_class', models.TextField(help_text='The class of the variant', null=True)),
                ('dbsnp_id', models.TextField(null=True)),
                ('strand', models.CharField(choices=[('+', '+'), ('-', '-')], max_length=1, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical variant',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
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
                ('id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('tissue', models.CharField(choices=[('unknown', 'unknown'), ('blood', 'blood'), ('hair', 'hair'), ('skin', 'skin'), ('amniotic fluid', 'amniotic fluid'), ('inside surface of the cheek', 'inside surface of the cheek')], default='unknown', max_length=27)),
                ('patient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='samples', to='core.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Transcript',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('ensembl_id', models.TextField(null=True)),
                ('refseq_id', models.TextField(null=True)),
                ('name', models.TextField()),
                ('hgvsg', models.TextField(null=True)),
                ('hgvsc', models.TextField(null=True)),
                ('hgvsp', models.TextField(null=True)),
                ('gene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transcripts', to='core.gene')),
            ],
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('vrs_id', models.TextField(null=True)),
                ('assembly', models.CharField(choices=[('GRCh38', 'GRCh38'), ('GRCh37', 'GRCh37')], max_length=6)),
                ('chromosome', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('X', 'X'), ('Y', 'Y')], max_length=2)),
                ('start', models.IntegerField(help_text='The start of the variant')),
                ('end', models.IntegerField(help_text='The end of the variant')),
                ('allele_string', models.TextField()),
                ('variant_class', models.TextField(help_text='The class of the variant', null=True)),
                ('dbsnp_id', models.TextField(null=True)),
                ('strand', models.CharField(choices=[('+', '+'), ('-', '-')], max_length=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VariantConsequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.TextField()),
                ('hr_term', models.TextField()),
                ('impact', models.CharField(choices=[('HIGH', 'HIGH'), ('MODERATE', 'MODERATE'), ('MODIFIER', 'MODIFIER'), ('LOW', 'LOW')], max_length=8)),
                ('description', models.TextField()),
                ('accession', models.CharField(max_length=10)),
                ('consequence_ranking', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='VariantEvidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('evidence', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='variant_evidences', to='core.evidence')),
                ('variant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='variant_evidences', to='core.variant')),
            ],
        ),
        migrations.CreateModel(
            name='VariantDisease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disease', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_diseases', to='core.disease')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_diseases', to='core.variant')),
            ],
        ),
        migrations.CreateModel(
            name='VariantAnnotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scope', models.CharField(max_length=50)),
                ('property', models.CharField(max_length=50)),
                ('value', models.JSONField(null=True)),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_annotations', to='core.variant')),
            ],
        ),
        migrations.AddField(
            model_name='variant',
            name='most_severe_consequence',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='variants', to='core.variantconsequence'),
        ),
        migrations.CreateModel(
            name='TranscriptEvidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('evidence', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transcript_evidences', to='core.evidence')),
                ('transcript', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transcript_evidences', to='core.transcript')),
            ],
        ),
        migrations.AddField(
            model_name='transcript',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transcripts', to='core.variant'),
        ),
        migrations.CreateModel(
            name='SampleVariantAnnotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scope', models.CharField(max_length=50)),
                ('property', models.CharField(max_length=50)),
                ('value', models.JSONField(null=True)),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sample_variant_annotations', to='core.sample')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sample_variant_annotations', to='core.variant')),
            ],
        ),
        migrations.CreateModel(
            name='SampleVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('zygosity', models.CharField(choices=[('Homozygous', 'Homozygous'), ('Heterozygous', 'Heterozygous'), ('Hemizygous', 'Hemizygous'), ('Homoplasmic', 'Homoplasmic'), ('Heteroplasmic', 'Heteroplasmic'), ('Zero_coverage_region', 'Zero_coverage_region')], default=None, max_length=20, null=True)),
                ('causative', models.BooleanField(default=False, help_text='If true This is a causative variant in this sample')),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sample_variants', to='core.sample')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sample_variants', to='core.variant')),
            ],
        ),
        migrations.CreateModel(
            name='Phenotype',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotations', models.JSONField(null=True)),
                ('custom_annotations', models.JSONField(null=True)),
                ('phenotype', models.TextField()),
                ('inheritance_modes', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), null=True, size=None)),
                ('gene', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.gene')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalVariantEvidence',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('evidence', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.evidence')),
            ],
            options={
                'verbose_name': 'historical variant evidence',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
