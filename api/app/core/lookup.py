
from typing import Callable


class DD(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Lookup():
    def __init__(self, choices: list, default: str=None, alias_choices: dict = None, validator: Callable = lambda v: True, clean: Callable = lambda v: v):
        self.__choices = self.__make_touples(choices)
        self.__default = default
        self.__alias_choices = alias_choices
        self.__validator = validator
        self.__clean = clean

    def __make_touples(self, values: list):
        return list(map(lambda v: (v, v), values))

    @property
    def max_length(self):
        return max(list(map(lambda c: len(c[0]), self.__choices)))

    @property
    def choices(self):
        return self.__choices

    @property
    def default(self):
        return self.__default

    @property
    def alias_choices(self):
        return self.__alias_choices

    @property
    def validator(self):
        return [self.__validator]

    @property
    def clean(self):
        return self.__clean

    def normalize(self, value):
        """ Normalizes the given value based on the lookup definition """
        # Translate choice aliases to the correct value
        if value in self.__alias_choices:
            return self.__alias_choices[value]

        return value


lookup = DD({
    'chromosome': Lookup(
        choices=list(map(lambda n: str(n), range(1, 23))) + ['X', 'Y']
    ),
    'assembly': Lookup(
        choices=['GRCh38', 'GRCh37'],
        alias_choices={'hg19': 'GRCh37', 'hg38': 'GRCh38'}
    ),
    'strand': Lookup(
        choices=['+', '-']
    ),
    'variant_consequence_impact': Lookup(
        choices=['HIGH', 'MODERATE', 'MODIFIER', 'LOW']
    ),
    'variant_type': Lookup(
        # the following list need to be adjusted to Ensembl
        choices=['SNV', 'CNV', 'DEL']
    ),
    'evidence_source': Lookup(
        choices=['Unknown', 'Pubmed', 'GoogleScholar', 'Internet', 'Internal'],
        default='Unknown'
    ),
    'zygosity': Lookup(
        choices=['Unknown', 'Homozygous', 'Heterozygous', 'Hemizygous', 'Homoplasmic', 'Heteroplasmic'],
        default='Unknown'
    ),
    'tissue': Lookup(
        choices=['unknown', 'blood', 'hair', 'skin', 'amniotic fluid', 'inside surface of the cheek'],
        default='unknown'
    ),
    'inheritance_mode': Lookup(
        choices=['AD', 'AR', 'DD', 'DR' 'MD', 'MR', 'XD', 'XR']
    )
})
