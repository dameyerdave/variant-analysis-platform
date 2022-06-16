from redis import Redis
import requests
from os import environ
from ga4gh.core import ga4gh_identify
from ga4gh.vrs import models
from ga4gh.vrs.dataproxy import SeqRepoRESTDataProxy
from modules.redis_cache import RedisCache
import json

VEP_API = 'https://rest.ensembl.org'
VEP_OLD_API = 'https://grch37.rest.ensembl.org'

VEP_OFFLINE_API = 'http://vep_rest:5005'

GENENAMES_API = 'http://rest.genenames.org/fetch/{}/{}'

ALLELE_REGISTRY_API = 'https://reg.genome.network/allele?hgvs={}'

SEQREPO_REST_SERVICE_URL = f"http://seqrepo:{environ.get('SEQREPO_PORT', 5000)}/seqrepo"

GNOMAD_URL = "https://gnomad.broadinstitute.org/api/"

OMIM_URL = f"https://api.omim.org/api/entry/search?apiKey={environ.get('OMIM_API_KEY', '2_y6sVJ5RaSk_jvrE_h9xw')}" + "&search=approved_gene_symbol:{}&format=json&retrieve=geneMap&start=0&limit=10"

DISGENET_API = 'http://disgenet:8000/api/vda/variants/{}'

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

def gnomad(variant_id, assembly='GRCh38'):
    payload = json.dumps({
    "query": "\nquery GnomadVariant($variantId: String!, $datasetId: DatasetId!, $referenceGenome: ReferenceGenomeId!, $includeLocalAncestry: Boolean!, $includeLiftoverAsSource: Boolean!, $includeLiftoverAsTarget: Boolean!) {\n  variant(variantId: $variantId, dataset: $datasetId) {\n    variant_id\n    reference_genome\n    chrom\n    pos\n    ref\n    alt\n    caid\n    colocated_variants\n    coverage {\n      exome {\n        mean\n      }\n      genome {\n        mean\n      }\n    }\n    multi_nucleotide_variants {\n      combined_variant_id\n      changes_amino_acids\n      n_individuals\n      other_constituent_snvs\n    }\n    exome {\n      ac\n      an\n      ac_hemi\n      ac_hom\n      faf95 {\n        popmax\n        popmax_population\n      }\n      filters\n      populations {\n        id\n        ac\n        an\n        ac_hemi\n        ac_hom\n      }\n      local_ancestry_populations @include(if: $includeLocalAncestry) {\n        id\n        ac\n        an\n      }\n      age_distribution {\n        het {\n          bin_edges\n          bin_freq\n          n_smaller\n          n_larger\n        }\n        hom {\n          bin_edges\n          bin_freq\n          n_smaller\n          n_larger\n        }\n      }\n      quality_metrics {\n        allele_balance {\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        genotype_depth {\n          all {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        genotype_quality {\n          all {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        site_quality_metrics {\n          metric\n          value\n        }\n      }\n    }\n    genome {\n      ac\n      an\n      ac_hemi\n      ac_hom\n      faf95 {\n        popmax\n        popmax_population\n      }\n      filters\n      populations {\n        id\n        ac\n        an\n        ac_hemi\n        ac_hom\n      }\n      local_ancestry_populations @include(if: $includeLocalAncestry) {\n        id\n        ac\n        an\n      }\n      age_distribution {\n        het {\n          bin_edges\n          bin_freq\n          n_smaller\n          n_larger\n        }\n        hom {\n          bin_edges\n          bin_freq\n          n_smaller\n          n_larger\n        }\n      }\n      quality_metrics {\n        allele_balance {\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        genotype_depth {\n          all {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        genotype_quality {\n          all {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        site_quality_metrics {\n          metric\n          value\n        }\n      }\n    }\n    flags\n    lof_curations {\n      gene_id\n      gene_symbol\n      verdict\n      flags\n      project\n    }\n    rsids\n    transcript_consequences {\n      domains\n      gene_id\n      gene_version\n      gene_symbol\n      hgvs\n      hgvsc\n      hgvsp\n      is_canonical\n      is_mane_select\n      is_mane_select_version\n      lof\n      lof_flags\n      lof_filter\n      major_consequence\n      polyphen_prediction\n      sift_prediction\n      transcript_id\n      transcript_version\n    }\n    in_silico_predictors {\n      id\n      value\n      flags\n    }\n  }\n\n  clinvar_variant(variant_id: $variantId, reference_genome: $referenceGenome) {\n    clinical_significance\n    clinvar_variation_id\n    gold_stars\n    last_evaluated\n    review_status\n    submissions {\n      clinical_significance\n      conditions {\n        name\n        medgen_id\n      }\n      last_evaluated\n      review_status\n      submitter_name\n    }\n  }\n\n  liftover(source_variant_id: $variantId, reference_genome: $referenceGenome) @include(if: $includeLiftoverAsSource) {\n    liftover {\n      variant_id\n      reference_genome\n    }\n    datasets\n  }\n\n  liftover_sources: liftover(liftover_variant_id: $variantId, reference_genome: $referenceGenome) @include(if: $includeLiftoverAsTarget) {\n    source {\n      variant_id\n      reference_genome\n    }\n    datasets\n  }\n\n  meta {\n    clinvar_release_date\n  }\n}\n",
    "variables": {
        "datasetId": "gnomad_r3",
        "includeLocalAncestry": True,
        "includeLiftoverAsSource": False,
        "includeLiftoverAsTarget": True,
        "referenceGenome": assembly,
        "variantId": variant_id
    }
    })

    headers = {
        'Content-Type': 'application/json'
    }

    cache = RedisCache()
    resp = cache.post(GNOMAD_URL, ignore_cache=False, headers=headers, data=payload)
    return resp

def omim(gene):
    cache = RedisCache()
    resp = cache.get(OMIM_URL.format(gene), ignore_cache=False)
    return resp

def disgenet(dbsnp_id):
    print("Try to get disease information from disgenet", DISGENET_API.format(dbsnp_id))
    resp = requests.get(DISGENET_API.format(dbsnp_id))
    print(resp)
    return resp