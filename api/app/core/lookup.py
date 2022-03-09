
from typing import Callable


class DD(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Lookup():
    def __init__(self, choices: list, validator: Callable = lambda v: True, clean: Callable = lambda v: v):
        self.__choices = self.__make_touples(choices)
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
    def validator(self):
        return [self.__validator]

    @property
    def clean(self):
        return self.__clean


lookup = DD({
    'chromosome': Lookup(
        choices=list(map(lambda n: str(n), range(1, 23))) + ['X', 'Y']
    ),
    'assembly': Lookup(
        choices=['GRCh38', 'GRCh37']
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
    )
})
