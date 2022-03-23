from __future__ import annotations
from django.db import models
from core.lookup import lookup
from django.contrib.postgres.fields import ArrayField


class Gene(models.Model):
    """ The gene model including flexible annotations """
    symbol = models.CharField(max_length=10, unique=True)
    ensembl_id = models.CharField(max_length=15, null=True)
    annotations = models.JSONField(null=True)

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


class Variant(models.Model):
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

    def __str__(self):
        return f"{self.assembly}: {self.chromosome}_{self.start}_{self.allele_string}"

    @property
    def extra(self):
        return {
            'most_severe_consequence': self.most_severe_consequence.hr_term,
        }


class Transcript(models.Model):
    """ The transcript model including flexible annotations """
    related_name = 'transcripts'

    name = models.TextField()
    ensembl_id = models.TextField(null=True)

    hgvsg = models.TextField(null=True)
    hgvsc = models.TextField(null=True)
    hgvsp = models.TextField(null=True)

    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    gene = models.ForeignKey(
        Gene, related_name=related_name, on_delete=models.CASCADE)

    annotations = models.JSONField(null=True)

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
