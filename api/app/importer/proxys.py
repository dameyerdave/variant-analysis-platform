import requests

VEP_API = 'https://rest.ensembl.org'
VEP_OLD_API = 'https://grch37.rest.ensembl.org'

GENENAMES_API = 'http://rest.genenames.org/fetch/{}/{}'


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


def genenames(symbol):
    for by in ['symbol', 'prev_symbol', 'alias_symbol']:
        try:
            resp = requests.get(GENENAMES_API.format(by, symbol), headers={
                "Accept": "application/json"})
            break
        except:
            continue

    return resp
