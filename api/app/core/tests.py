from rest_framework.test import APITestCase
from rest_framework import status


class TestSerializers(APITestCase):
    fixtures = ['variant_consequences']
    def setUp(self):
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
