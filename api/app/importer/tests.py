from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from importer.evidence_providers import PubMedEvidenceProvider
from importer.proxys import vrs, vrs_sequence_identifier


class TestViews(APITestCase):
    fixtures = ['variant_consequences']
    def test_add_vep_variant_view(self):
        response = self.client.get(
            '/api/import/vep/region/7_140453136_A_T?assembly=GRCh37')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['input'], '7\t140453136\t.\tA\tT')

    def test_add_vep_variant_view_invalid_region(self):
        response = self.client.get(
            '/api/import/vep/region/7_140453136?assembly=GRCh37')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_add_vep_variant_view_bad_request(self):
        response = self.client.get(
            '/api/import/vep/region/7_140453136_?assembly=GRCh37')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

class TestEvidenceProviders(TestCase):
    def test_pubmed_evidence_provider(self):
        PMID=17418584
        provider = PubMedEvidenceProvider()
        result = provider.fetch(pmid=PMID)

        self.assertEqual(isinstance(result, dict), True)
        self.assertEqual(result['source'], 'Pubmed')
        self.assertEqual(result['reference'], PMID)

class TestProxies(TestCase):
    def test_vrs_proxy(self):
        SEQUENCE_IDENTIFIER='GRCh38:19'
        EXPECTED_VRS_IDENTIFIER='ga4gh:GS.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl'
        ALLELE='T'
        START=44908821
        END=44908822
        EXPECTED_VRS='ga4gh:VA.EgHPXXhULTwoP4-ACfs-YCXaeUQJBjH_'

        vrs_identifier = vrs_sequence_identifier(SEQUENCE_IDENTIFIER)
        self.assertEqual(vrs_identifier, EXPECTED_VRS_IDENTIFIER)

        result = vrs(SEQUENCE_IDENTIFIER, allele=ALLELE, start=START, end=END)
        self.assertEqual(result, EXPECTED_VRS)

        

