import requests

API = 'https://rest.ensembl.org'
OLD_API = 'https://grch37.rest.ensembl.org'


def vep(input, species='human', input_type='hgvs', GRCh37=False, refseq=False):
    req = f"{API if not GRCh37 else OLD_API}/vep/{species}/{input_type}/{input}"
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
