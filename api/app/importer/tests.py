from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status


class TestViews(APITestCase):
    def test_add_vep_variant_view(self):
        response = self.client.get(
            '/api/import/vep/region/7_140453136_T?assembly=GRCh37')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data[0]['input'], '7 140453136 140453136 A/T 1')

    def test_add_vep_variant_view_invalid_region(self):
        response = self.client.get(
            '/api/import/vep/region/7_140453136?assembly=GRCh37')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_add_vep_variant_view_bad_request(self):
        response = self.client.get(
            '/api/import/vep/region/7_140453136_?assembly=GRCh37')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
