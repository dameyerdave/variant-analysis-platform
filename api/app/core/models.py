from __future__ import annotations
from django.db import models
from django.db.models import F
from django.core import validators
from django.forms import CharField
from core.lookup import lookup
from django.contrib.postgres.fields import ArrayField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone as tz
from simple_history.models import HistoricalRecords
from config.config import Config
from core.helpers import q_from_config

class FilterManager(models.Manager):
    def filtered(self, filter):
        if not filter:
            # We set the default filter
            filter = 'default'
        config = Config().as_dict()
        model_name = self.model.__name__.lower()
        # print('FilterManager: model_name', model_name)
        if model_name in config and 'filters' in config[model_name] and filter in config[model_name]['filters']:
            _filter = q_from_config(config[model_name]['filters'][filter])
            # print('_filter', _filter)
            return super().get_queryset().filter(_filter).distinct()
        else:
            return super().get_queryset().all()

class TimeTrackedModel(models.Model):
    created_at = models.DateTimeField(default=tz.now)

    class Meta:
        abstract = True

class AnnotationModel(models.Model):
    annotations = models.JSONField(null=True)
    custom_annotations = models.JSONField(null=True)

    class Meta:
        abstract = True
        
class Evidence(AnnotationModel):
    related_name='evidences'

    reference = models.TextField()
    source = models.CharField(
        max_length=lookup.evidence_source.max_length, 
        choices=lookup.evidence_source.choices, 
        default=lookup.evidence_source.default
    )
    title = models.TextField()
    summary = models.TextField()
    evidence_date = models.DateTimeField()

class Gene(AnnotationModel):
    """ The gene model including flexible annotations """
    symbol = models.CharField(max_length=20, unique=True)
    ensembl_id = models.CharField(max_length=15, null=True)

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

    def __str__(self):
        return self.symbol

    class Meta:
        ordering = ['symbol']


class VariantConsequence(models.Model):
    """ The lookup for VEP variant consequences """
    term = models.TextField()
    hr_term = models.TextField()
    impact = models.CharField(
        max_length=lookup.variant_consequence_impact.max_length, choices=lookup.variant_consequence_impact.choices)
    description = models.TextField()
    accession = models.CharField(max_length=10)

    def __str__(self):
        return self.term

    class Meta:
        ordering = ['term']


class Variant(AnnotationModel):
    """ The variant model """
    related_name = 'variants'

    assembly = models.CharField(
        max_length=lookup.assembly.max_length, choices=lookup.assembly.choices)
    chromosome = models.CharField(
        max_length=lookup.chromosome.max_length, choices=lookup.chromosome.choices)
    start = models.IntegerField(help_text='The start of the variant')
    end = models.IntegerField(help_text='The end of the variant')
    allele_string = models.TextField()

    strand = models.CharField(
        max_length=lookup.strand.max_length, choices=lookup.strand.choices)
    most_severe_consequence = models.ForeignKey(
        VariantConsequence, related_name=related_name, null=True, on_delete=models.SET_NULL)

    variant_type = models.CharField(
        max_length=lookup.variant_type.max_length, choices=lookup.variant_type.choices)

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

    def __str__(self):
        return f"{self.assembly}: {self.chromosome}_{self.start}_{self.allele_string}"

    @property
    def extra(self):
        return {
            'most_severe_consequence': self.most_severe_consequence.hr_term
        }

    class Meta:
        unique_together = ('chromosome', 'start', 'end', 'allele_string')


class Transcript(AnnotationModel):
    """ The transcript model including flexible annotations """
    related_name = 'transcripts'

    ensembl_id = models.TextField(null=True, unique=True)
    name = models.TextField()

    hgvsg = models.TextField(null=True)
    hgvsc = models.TextField(null=True)
    hgvsp = models.TextField(null=True)

    variant = models.ForeignKey(Variant, related_name=related_name, on_delete=models.CASCADE)
    gene = models.ForeignKey(
        Gene, related_name=related_name, on_delete=models.CASCADE)
    
    # 0 means not ranked, rank 1 is best 2 second best ...
    # basically this could be done based on the canonical flag or any other logic
    rank = models.PositiveIntegerField(default=0)

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

    def __str__(self):
        return f"{self.variant} | {self.ensembl_id} ({self.gene})"

    @property
    def hgvsg(self):
        return f"{self.variant.chromosome}:{self.variant.start}{self.variant.allele_string.replace('/', '>')}",

    @property
    def extra(self):
        return {
            'variant': str(self.variant),
            'gene': str(self.gene),
            'hgvsg': self.hgvsg
        }

class TranscriptEvidence(TimeTrackedModel):
    related_name = 'transcript_evidences'
    
    transcript = models.ForeignKey(Transcript, related_name=related_name, null=True, on_delete=models.SET_NULL)
    evidence = models.ForeignKey(Evidence, related_name=related_name, null=True, on_delete=models.SET_NULL)

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

    class Meta:
        unique_together = ('transcript', 'evidence')


class Patient(models.Model):
    related_name = 'patients'

    prename = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    surename = models.CharField(max_length=50)

    street = models.CharField(max_length=50)
    house_number = models.IntegerField(
        validators=[validators.MinValueValidator(1)])

    zip = models.IntegerField(validators=[validators.MinValueValidator(1000)])
    place = CharField(max_length=50)

    phone = PhoneNumberField()
    email = models.EmailField()

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

class Sample(models.Model):
    related_name = 'samples'

    id = models.CharField(max_length=20, primary_key=True)
    patient = models.ForeignKey(Patient, related_name=related_name, null=True, on_delete=models.SET_NULL)

    tissue = models.CharField(max_length=lookup.tissue.max_length, choices=lookup.tissue.choices, default=lookup.tissue.default)

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

class SampleVariant(models.Model):
    related_name = 'sample_variants'

    sample = models.ForeignKey(Sample, related_name=related_name, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, related_name=related_name, on_delete=models.CASCADE)

    # Specific fields for variants in samples
    zygosity = models.CharField(max_length=lookup.zygosity.max_length, choices=lookup.zygosity.choices, default=lookup.zygosity.default)

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

    class Meta:
        unique_together = ['sample', 'variant']

class Phenotype(AnnotationModel):
    gene = models.ForeignKey(Gene, null=True, on_delete=models.SET_NULL)
    phenotype = models.TextField()
    inheritance_mode = models.CharField(max_length=lookup.inheritance_mode.max_length, choices=lookup.inheritance_mode.choices)

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()
