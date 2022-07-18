from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from os import environ


class TestSerializers(APITestCase):
    fixtures = ['variant_consequences']

    def setUp(self):
        user = get_user_model().objects.create_user(email=environ.get('DJANGO_SU_EMAIL'), password='secret')
        self.client.force_login(user)

        self.default_variant = {
            "assembly": "GRCh38",
            "chromosome": 7,
            "start": 140453136,
            "end": 140453136,
            "allele_string": "A/T",
            "strand": "-",
            "most_severe_consequence": 11,  # missense_variant
            "variant_class": "SNV"
        }

    def test_variant_serializer_normalize_assembly(self):
        variant = self.default_variant.copy()
        variant.update({'assembly': 'hg19'})
        response = self.client.post(
            '/api/variants/', variant)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['assembly'], 'GRCh37')
