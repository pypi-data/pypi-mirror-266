import re
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

from strideutils import stride_requests
from strideutils.stride_config import config


@dataclass
class TxResponse:
    stdout: str
    stderr: str
    tx_response: Optional[dict] = None
    tx_hash: Optional[str] = None
    success: bool = False
    raw_log: Optional[str] = None


def execute_tx(command: str, api_endpoint: str = config.stride.api_endpoint) -> TxResponse:
    """
    Execute a tx and query the tx hash
    """
    output = subprocess.run(command, shell=True, capture_output=True)
    standard_out = re.sub(r'\x1b\[[0-9;]*[mGKH]', '', output.stdout.decode('utf-8'))
    error_out = re.sub(r'\x1b\[[0-9;]*[mGKH]', '', output.stderr.decode('utf-8'))

    tx_hash = ""
    for output_line in standard_out.split('\n'):
        if 'txhash' in output_line:
            tx_hash = output_line.split(': ')[-1]

    tx_response = None
    response_success = False
    raw_log = ""
    if not error_out:
        event_filters = [(f"tx.hash='{tx_hash}'")]
        for _ in range(15):
            time.sleep(2)
            tx_response = stride_requests.get_txs(event_filters, api_endpoint)
            if tx_response['total'] != '0':
                try:
                    response_code = tx_response['tx_responses'][0]['code']
                    raw_log = tx_response['tx_responses'][0]['raw_log']
                    response_success = response_code == 0
                except KeyError:
                    response_success = False
                break

    success = response_success and not error_out
    response = TxResponse(
        stdout=standard_out,
        stderr=error_out,
        tx_response=tx_response,
        success=success,
        tx_hash=tx_hash,
        raw_log=raw_log,
    )
    return response
