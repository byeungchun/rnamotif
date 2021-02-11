"""Ensembel REST API helper"""
import os
import json
import time
import logging
import requests

logger = logging.getLogger(__name__)
# c_handler = logging.StreamHandler()
# c_handler.setLevel(logging.DEBUG)
# c_format = logging.Formatter('%(levelname)s - %(message)s')
# logger.addHandler(c_handler)

MAX_RETRY = 5
ENSEMBL_API_URL = "https://rest.ensembl.org/sequence/id/"
HEADER = {"Content-Type": "text/plain"}


def get_ensembl_seq_by_gene(
    lst_gene: list,
    seq_type: str = 'genomic',
    is_ssl_verification: bool = True
) -> json:
    """Retreive Genome sequence using Ensembl REST API 
    It requires two user inputs (List of target genes, Sequence type)
    Sequence type should be one of fours - genomic, cds, cdna, protein

    Args:
        lst_gene: list of target genes
        seq_type: sequnce type - genomic, cds, cdna, protein
        is_ssl_verification: Network doesn't support SSL verification, set it to False
    Returns:
        json: Sequence data (two levels - Target, Sequence type)
    """

    res = dict()
    for i, gene in enumerate(lst_gene):
        num_retry = 0
        flag_req_success = False
        res[gene] = dict()
        param = f'{gene}?type={seq_type}'
        req_url = f'{ENSEMBL_API_URL}{param}'

        try:
            while num_retry < MAX_RETRY:
                # Request API service
                ret = requests.get(req_url, headers=HEADER,
                                   verify=is_ssl_verification)
                if ret.status_code == 200:
                    flag_req_success = True
                elif ret.status_code in [400, 404]:
                    res[gene][seq_type] = json.loads(ret.text)
                elif ret.status_code in [403, 408, 429]:
                    logger.info(
                        f"Ensembl API server is not working for {req_url}.\nWait 5 seconds and retry. # of retries: {num_retry}/{MAX_RETRY}")
                    time.sleep(5)
                    num_retry += 1
                    continue
                elif ret.status_code == 503:
                    logger.error(f'Error({ret.status_code}): {ret.text}')
                else:
                    logger.error(
                        f'Unknown server status code({ret.status_code})')

                res[gene][seq_type] = {
                    'retsts': flag_req_success,
                    'requrl': req_url,
                    'retval': ret.text
                }
                break
        except Exception as ex:
            raise RuntimeError(f'Ensembl API request error.\n{ex}')
            return res
        print(f'{i} - {req_url}')

    return res
