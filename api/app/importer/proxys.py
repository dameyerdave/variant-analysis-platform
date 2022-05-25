import requests
from os import environ
from ga4gh.core import ga4gh_identify
from ga4gh.vrs import models
from ga4gh.vrs.dataproxy import SeqRepoRESTDataProxy

VEP_API = 'https://rest.ensembl.org'
VEP_OLD_API = 'https://grch37.rest.ensembl.org'

VEP_OFFLINE_API = 'http://vep_rest:5005'

GENENAMES_API = 'http://rest.genenames.org/fetch/{}/{}'

ALLELE_REGISTRY_API = 'https://reg.genome.network/allele?hgvs={}'

SEQREPO_REST_SERVICE_URL = f"http://seqrepo:{environ.get('SEQREPO_PORT', 5000)}/seqrepo"


def vep(input, species='human', input_type='hgvs', GRCh37=False, refseq=False):
    req = f"{VEP_API if not GRCh37 else VEP_OLD_API}/vep/{species}/{input_type}/{input}"
    params = {
        'canonical': True,
        'hgvs': True,
        'SpliceRegion': True,
        'ccds': True,
        'tls': True,
        'xref_refseq': True
    }
    if refseq:
        params['refseq'] = True

    resp = requests.get(req, headers={
        'Content-Type': 'application/json'
    }, params=params)

    return resp

def vep_offline(input, **vep_options):
    req = f"{VEP_OFFLINE_API}"

    params={
        'q': input,
    }
    params.update(vep_options)
    resp = requests.get(req, headers={
        'Content-Type': 'application/json'
    }, params=params)

    return resp


def genenames(symbol):
    for by in ['symbol', 'prev_symbol', 'alias_symbol']:
        try:
            resp = requests.get(GENENAMES_API.format(by, symbol), headers={
                "Accept": "application/json"})
            break
        except:
            continue

    return resp


def alleleregistry(hgvs):
    try:
        resp = requests.get(ALLELE_REGISTRY_API.format(hgvs), headers={
            "Accept": "application/json"})
    except:
        pass

    return resp


def vrs_sequence_identifier(sequence_id):
    """ Returns the vrs identifier from seqrepo based on assembly:chromosome """
    _seqrepo = SeqRepoRESTDataProxy(base_url=SEQREPO_REST_SERVICE_URL)
    return _seqrepo.translate_sequence_identifier(sequence_id, "ga4gh")[0]
    

def vrs(vep_info):
    """ Returns the VRS identifier of a variant based on the vep_info"""
    sequence_id = f"{vep_info.get('assembly_name')}:{vep_info.get('seq_region_name')}"
    allele = vep_info.get('allele_string').split('/')[1] if '/' in vep_info.get('allele_string') else vep_info.get('allele_string')
    start = vep_info.get('start')
    end = vep_info.get('end')
    if end is None or start == end:
        end = start
        start = start - 1
    try:
        _sequence_id = vrs_sequence_identifier(sequence_id)
        _interval = models.SimpleInterval(start=start, end=end)
        _location = models.SequenceLocation(
            sequence_id=_sequence_id, interval=_interval)
        # _location['_id'] = ga4gh_identify(_location)
        _state = models.SequenceState(sequence=allele)
        _allele = models.Allele(location=_location, state=_state)
        # dj(_allele)
    except Exception as ex:
        raise Exception(
            f"Cannot query local seqrepo server. Check if the container 'seqrepo_local' is running: {ex}")

    return ga4gh_identify(_allele)
