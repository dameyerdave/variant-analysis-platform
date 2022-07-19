from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from importer.evidence_providers import PubMedEvidenceProvider
from importer.proxys import vrs, vrs_sequence_identifier, disgenet, vep_offline
from django.contrib.auth import get_user_model
from os import environ

class TestViews(APITestCase):
    fixtures = ['variant_consequences']

    def setUp(self):
        user = get_user_model().objects.create_user(email=environ.get('DJANGO_SU_EMAIL'), password='secret')
        self.client.force_login(user)

    def test_add_vep_variant_view(self):
        """ Test the variant import over the view works """
        response = self.client.get(
            '/api/import/vep/region/7_140453136_A_T?assembly=GRCh37')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['allele_string'], 'A/T')

    def test_add_vep_variant_view_invalid_region1(self):
        """ Test the variant import over the view returns an error if the variant nomenclature is wrong """
        response = self.client.get(
            '/api/import/vep/region/7_140453136?assembly=GRCh37')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_add_vep_variant_view_invalid_region2(self):
        """ Test the variant import over the view returns an error if the variant nomenclature is wrong """
        response = self.client.get(
            '/api/import/vep/region/7_140453136_?assembly=GRCh37')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

class TestEvidenceProviders(TestCase):
    def test_pubmed_evidence_provider(self):
        """ Test if the pmid evidence provider works """
        PMID=17418584
        provider = PubMedEvidenceProvider()
        result = provider.fetch(pmid=PMID)

        self.assertEqual(isinstance(result, dict), True)
        self.assertEqual(result['source'], 'Pubmed')
        self.assertEqual(result['reference'], PMID)

class TestProxies(TestCase):
    def test_vrs_proxy(self):
        """ Test if the vrs proxy works """
        ASSEMBLY='GRCh38'
        CHROMOSOME=19
        SEQUENCE_IDENTIFIER=f"{ASSEMBLY}:{CHROMOSOME}"
        REF='A'
        ALT='T'
        START=44908821
        EXPECTED_VRS_IDENTIFIER='ga4gh:SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl'
        EXPECTED_VRS='ga4gh:VA.7BBsP_2LgHA4RXa05D7Y4JoQuz0g2lMR'

        vrs_identifier = vrs_sequence_identifier(SEQUENCE_IDENTIFIER)
        self.assertEqual(vrs_identifier, EXPECTED_VRS_IDENTIFIER)

        try:
            vep_resp = vep_offline(f"{CHROMOSOME}_{START}_{REF}_{ALT}", assembly=ASSEMBLY)
            self.assertEqual(vep_resp.status_code, 200)
            if vep_resp.ok:
                vep_info = vep_resp.json()[0]
                result = vrs(vep_info)
                self.assertEqual(result, EXPECTED_VRS)
        except Exception as ex:
            self.fail(f"Failed with {ex}")

    def test_disgenet(self):
        """ Test if the disgenet proxy works """
        VARIANT_ID='rs104893837'
        DISEASE_IDS=('C0342384', 'C0028960', 'C0342538', 'C1563719', 'C3899503', 'C0271623')
        resp = disgenet(VARIANT_ID)
        self.assertEqual(resp.status_code, 200)
        if resp.ok:
            data = resp.json()
            self.assertEqual(data['variantid'], VARIANT_ID)
            self.assertEqual(len(data['diseases']), len(DISEASE_IDS), 'Number of diseases returned differs from the expected number')
            for disease in data['diseases']:
                self.assertIn(disease['diseaseid'], DISEASE_IDS, 'Disease id is not in the list of expected disease ids')

        

