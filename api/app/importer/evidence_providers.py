from time import strptime
import xmltodict
from datetime import datetime as dt
from django.utils.timezone import make_aware
from modules.redis_cache import RedisCache
from friendlylog import colored_logger as log


class EvidenceProvider():
    """ Queries an evidence source and returns an Evidence Object or None if nothing could be found."""
    def __init__(self):
        self.cache = RedisCache()
    
    def fetch(self, **params):
      raise NotImplementedError("You must implement fetch for an EvidenceProvider.")

class PubMedEvidenceProvider(EvidenceProvider):
    URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&retmode=xml&rettype=vcv&is_variation_id'
    
    def fetch(self, **params):
        evidence = None
        try:
            req = self.URL.format(params['pmid'])
            resp = self.cache.get(req, headers={
                'Content-Type': 'application/json'
            }, params=params)

            if resp.ok:
                data = xmltodict.parse(resp.content)
                try:
                    evidence = {
                        'source': 'Pubmed',
                        'reference': params['pmid'],
                        'title': data['PubmedArticleSet']['PubmedArticle']['MedlineCitation']['Article']['ArticleTitle'],
                        'summary': self.__get_summary(data['PubmedArticleSet']['PubmedArticle']['MedlineCitation']['Article']),
                        'evidence_date': make_aware(dt.strptime("{Year}-{Month}-{Day}".format(**data['PubmedArticleSet']['PubmedArticle']['MedlineCitation']['DateRevised']), '%Y-%m-%d'))
                    }
                except KeyError as ke:
                    log.warning(ke, data)
        except Exception as ex:
            log.warning(ex)

        return evidence

    def __get_summary(self, article):
        if not 'Abstract' in article:
            return ''

        abstract_texts = article['Abstract']['AbstractText']
        if isinstance(abstract_texts, str):
            return abstract_texts

        if isinstance(abstract_texts, list):
            summary = ''
            for abstract_text in abstract_texts:
                if isinstance(abstract_text, dict):
                    summary += abstract_text.get('@Label')
                    summary += '\n'
                    summary += abstract_text.get('#text')
                    summary += '\n'
            return summary
