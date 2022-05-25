from __future__ import annotations
from django.db import models
from django.db.models import Q
from django.contrib.postgres.aggregates import BoolAnd
from django.core import validators
from django.forms import CharField
from core.lookup import lookup
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone as tz
from simple_history.models import HistoricalRecords
from config.config import Config
from core.helpers import q_from_config

class FilterManager(models.Manager):
    def filtered(self, _filter = None, ordering = None, flags = True):
        config = Config().as_dict()
        model_name = self.model.__name__.lower()

        # Apply filters
        if _filter:
            if model_name in config and 'filters' in config[model_name] and _filter in config[model_name]['filters']:
                filter = q_from_config(config[model_name]['filters'][_filter])
                qs = super().get_queryset().filter(filter).distinct()
            else:
                # in case there is no filter defined in the config return all objects
                qs = super().get_queryset().all()
        else:
            # in case there is no filter defined in the request params return all objects
            qs = super().get_queryset().all()

        # Annotate flags
        if flags:
            if model_name in config and 'flags' in config[model_name]:
                flags = config[model_name]['flags']
                for flag, flag_definition in flags.items():
                    rule = q_from_config(flag_definition['rule'])
                    qs = qs.annotate(**{f"flag_{flag}": BoolAnd(rule)})

        # Order the queryset
        if ordering:
            qs = qs.order_by(*ordering)

        return qs

class TimeTrackedModel(models.Model):
    """ 
    A timetracked model. Supports a created_at property 
    containing the timestamp of the creation time. 
    """
    created_at = models.DateTimeField(default=tz.now)

    class Meta:
        abstract = True

class AnnotationModel(models.Model):
    """ A model that supports annotations, custom_annotations and flags """
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

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

    class Meta:
        unique_together = ('reference', 'source')

class Gene(AnnotationModel):
    """ The gene model including flexible annotations """
    symbol = models.CharField(max_length=20, unique=True)
    ensembl_id = models.CharField(max_length=15, null=True)
    entrez_id = models.IntegerField(null=True)

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

    def __str__(self):
        return self.symbol


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



class Variant(AnnotationModel):
    """ The variant model """
    related_name = 'variants'

    vrs_id = models.TextField(null=True)

    assembly = models.CharField(
        max_length=lookup.assembly.max_length, choices=lookup.assembly.choices)
    chromosome = models.CharField(
        max_length=lookup.chromosome.max_length, choices=lookup.chromosome.choices)
    start = models.IntegerField(help_text='The start of the variant')
    end = models.IntegerField(help_text='The end of the variant')
    allele_string = models.TextField()
    variant_class = models.TextField(null=True, help_text='The class of the variant')

    strand = models.CharField(
        max_length=lookup.strand.max_length, choices=lookup.strand.choices, null=True)
    most_severe_consequence = models.ForeignKey(
        VariantConsequence, related_name=related_name, null=True, on_delete=models.SET_NULL)

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
        unique_together = ('assembly', 'chromosome', 'start', 'end', 'allele_string')


class Transcript(AnnotationModel):
    """ The transcript model including flexible annotations """
    related_name = 'transcripts'

    variant=models.ForeignKey(Variant, related_name=related_name, on_delete=models.CASCADE)

    ensembl_id = models.TextField(null=True)
    refseq_id = models.TextField(null=True)

    name = models.TextField()

    hgvsg = models.TextField(null=True)
    hgvsc = models.TextField(null=True)
    hgvsp = models.TextField(null=True)

    gene = models.ForeignKey(
        Gene, related_name=related_name, on_delete=models.CASCADE)

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

    def __str__(self):
        return f"{self.ensembl_id} ({self.gene})"

    @property
    def extra(self):
        return {
            'gene': str(self.gene),
        }

    class Meta:
        unique_together=('variant', 'ensembl_id')

class TranscriptEvidence(TimeTrackedModel):
    related_name = 'transcript_evidences'
    
    transcript = models.ForeignKey(Transcript, related_name=related_name, null=True, on_delete=models.SET_NULL)
    evidence = models.ForeignKey(Evidence, related_name=related_name, null=True, on_delete=models.SET_NULL)

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

    class Meta:
        unique_together = ('transcript', 'evidence')

class VariantEvidence(TimeTrackedModel):
    related_name = 'variant_evidences'
    
    variant = models.ForeignKey(Variant, related_name=related_name, null=True, on_delete=models.SET_NULL)
    evidence = models.ForeignKey(Evidence, related_name=related_name, null=True, on_delete=models.SET_NULL)

    history = HistoricalRecords(inherit = True)
    objects = FilterManager()

    class Meta:
        unique_together = ('variant', 'evidence')


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

class SampleVariant(AnnotationModel):
    related_name = 'sample_variants'

    sample = models.ForeignKey(Sample, related_name=related_name, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, related_name=related_name, on_delete=models.CASCADE)

    # # Specific fields for variants in samples
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
