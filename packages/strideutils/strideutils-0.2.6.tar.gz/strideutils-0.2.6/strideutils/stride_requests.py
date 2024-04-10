import base64
import datetime
import json
import time
import urllib.parse
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import bech32
import dateutil.parser
import pandas as pd
import pytz
import requests
from requests.adapters import HTTPAdapter, Retry

from strideutils import stride_upstash
from strideutils.stride_config import config

ACCOUNT_QUERY = "cosmos/auth/v1beta1/accounts/{address}"
ACCOUNT_BALANCE_QUERY = "cosmos/bank/v1beta1/balances/{address}"
ACCOUNT_DELEGATIONS_QUERY = "cosmos/staking/v1beta1/delegations/{delegator_address}"
ACCOUNT_UNBONDINGS_QUERY = "cosmos/staking/v1beta1/delegators/{delegator_address}/unbonding_delegations"
MODULE_ACCOUNTS_QUERY = "cosmos/auth/v1beta1/module_accounts"
SUPPLY_QUERY = "cosmos/bank/v1beta1/supply/by_denom"

TXS_QUERY = "cosmos/tx/v1beta1/txs"
TX_BY_ACCOUNT_EVENT = "tx.acc_seq='{address}/{sequence}'"

HOST_ZONE_QUERY = "Stride-Labs/stride/stakeibc/host_zone"
EPOCHS_QUERY = "Stridelabs/stride/epochs"

RATE_LIMIT_QUERY = "Stride-Labs/ibc-rate-limiting/ratelimit/ratelimits"

STAKETIA = "staketia"
STAKEDYM = "stakedym"

MULTISIG_HOST_ZONE_QUERY = "Stride-Labs/stride/{module}/host_zone"
MULTISIG_DELEGATION_RECORDS_QUERY = "Stride-Labs/stride/{module}/delegation_records"
MULTISIG_UNBONDING_RECORDS_QUERY = "Stride-Labs/stride/{module}/unbonding_records"
MULTISIG_REDEMPTION_RECORDS_QUERY = "Stride-Labs/stride/{module}/redemption_records"

COSMWASM_CONTRACT_QUERY = "cosmwasm/wasm/v1/contract/{contract_address}/smart/{query}"

requests_session = requests.Session()

retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[400, 403, 404, 500, 502, 503, 504])

requests_session.mount("http://", HTTPAdapter(max_retries=retries))
requests_session.mount("https://", HTTPAdapter(max_retries=retries))


def request(
    url: str,
    headers: dict = {},
    params: Union[dict, List[Tuple[str, str]]] = {},
    block_height: int = 0,
    cache_response: bool = False,
    _cache: Dict[str, Any] = {},
):
    """
    This returns a JSON output from the given URL, and then parses the JSON output
    returning the field specified by json_path

    E.g. request(
        "https://lcd.osmosis.zone/osmosis/mint/v1beta1/params",
        ["params", "distribution_proportions", "community_pool"]
    ) = 0.05

    If cache is true, will save the output for the future.
    """
    cache_key = f"{url}{headers}{params}{block_height}"
    if cache_key in _cache:
        return _cache[cache_key]

    headers = headers or {}
    headers["x-cosmos-block-height"] = str(block_height)
    headers["Content-Type"] = "application/json"

    # Both dictionaries and tuples are supported for params, in case
    # the same key needs to be repeated
    if type(params) is dict:
        params = list(params.items())

    resp = requests_session.get(url, headers=headers, params=params)
    if not resp.ok:  # resp.ok is true if state_code is less than 400
        print(f"Error fetching {url}: {resp.status_code} {resp.json()}")
        raise Exception(f"Error fetching {url}: {resp.status_code} {resp.json()}")

    out = resp.json()
    if cache_response:
        _cache[cache_key] = out
    return out


def query_list_with_pagination(
    endpoint: str,
    rel_key: str,
    block_height: int = 0,
    max_pages: int = 50,
) -> List[Dict]:
    """
    Query a list with pagination
    Returns the concatenated list from all the responses
    """
    data = []
    query_url = endpoint
    query_count = 0

    while True:
        res = request(url=query_url, block_height=block_height)
        data += res[rel_key]

        query_count += 1
        if query_count >= max_pages:
            print(f"Max pages {max_pages} reached - results are truncated")
            break

        # Break if it's a paginated query
        if "pagination" not in res.keys():
            break

        # Continue looping as long as the pagination key is not null
        pagination_key = res["pagination"]["next_key"]
        if not pagination_key:
            break

        # Update query url with next key
        encoded_pagination_key = urllib.parse.quote_plus(pagination_key)
        query_url = f"{endpoint}?pagination.key={encoded_pagination_key}"

    return data


def get_all_host_zones() -> List[Dict]:
    """
    Queries all host zone structs, returning a list of each host zone json

    Returns:
        A list of host zone structs
            e.g. [{'chain_id': 'comdex-1',
                  'bech32prefix': 'comdex',
                  'connection_id': 'connection-28',
                  'transfer_channel_id': 'channel-49',
                  'ibc_denom':
                      'ibc/EB66980014602E6BD50A1CB9FFB8FA694DC3EC10A48D2C1C649D732954F88D4A',
                  'host_denom': 'ucmdx',
                  'unbonding_period': '21',
                  'validators': [
                      {'name': 'autostake',
                       'address': 'comdexvaloper195re7mhwh9urewm3rvaj9r7vm6j63c4sd78njd',
                       'weight': '4065',
                       'delegation': '227025044931',
                       'slash_query_progress_tracker': '0',
                       'slash_query_checkpoint': '32170217709',
                       'shares_to_tokens_rate': '1.000000000000000000',
                       'delegation_changes_in_progress': '0',
                       'slash_query_in_progress': False}, ...more validators]
                  'deposit_address':
                      'stride1ayccyk99tdu2ly2xuafuhwexqrwwxj3c58yueccn28gp4p3cm7ysajdr5w',
                  'withdrawal_ica_address':
                      'comdex1frwz448nerqg0cvt2277mua3gu6tw5tu85csst270klagenw47lsrlnn85',
                  'fee_ica_address':
                      'comdex16gsggz28xvam6sq5qu6llthg2nrwdx3w0guluhh6afgdpssel3pqgpzlag',
                  'delegation_ica_address':
                      'comdex1qj6rdc6qwqnat5scej42299meeke455gpxy4cyan7ktfasd3wt5q06dyv6',
                  'redemption_ica_address':
                      'comdex1p4pkh5af7fdyhk2ug8zg9xtgwyypgj2ejqwgkklty3u9usx2wgvqqu663c',
                  'total_delegations': '3931191365862',
                  'last_redemption_rate': '1.162131533280880561',
                  'redemption_rate': '1.162388595082765474',
                  'min_redemption_rate': '1.033653977192886878',
                  'max_redemption_rate': '1.196862499907553227',
                  'min_inner_redemption_rate': '1.138890000000000000',
                  'max_inner_redemption_rate': '1.171390000000000000',
                  'lsm_liquid_stake_enabled': False,
                  'halted': False},
                  ...more host zones]

    """
    endpoint = f"{config.stride.api_endpoint}/{HOST_ZONE_QUERY}"
    response = request(endpoint)
    host_zones = response["host_zone"]

    return host_zones


def _cast_host_zone_fields(host_zone: Dict[str, Any]) -> Dict[str, Any]:
    """
    Casts the host zone int and float types
    """
    float_columns = [
        "redemption_rate",
        "min_redemption_rate",
        "max_redemption_rate",
        "min_inner_redemption_rate",
        "max_inner_redemption_rate",
        "total_delegations",
    ]
    int_columns = ["unbonding_period", "delegated_balance"]

    for column in [c for c in float_columns if c in host_zone]:
        host_zone[column] = float(host_zone[column])
    for column in [c for c in int_columns if c in host_zone]:
        host_zone[column] = int(host_zone[column])

    return host_zone


def get_host_zone_json(zone_id: str, cast_types: bool = True, **kwargs) -> Dict[str, Any]:
    """
    Queries a stakeibc host zone, returning a dict with the host zone structure and fields casted
    """
    if zone_id == "celestia":
        return get_celestia_host_zone(cast_types=cast_types)
    if zone_id == "dymension_1100-1":
        return get_dymension_host_zone(cast_types=cast_types)

    endpoint = f"{config.stride.api_endpoint}/Stride-Labs/stride/stakeibc/host_zone/{zone_id}"
    host_zone = request(endpoint, **kwargs)["host_zone"]

    if cast_types:
        host_zone = _cast_host_zone_fields(host_zone)

    return host_zone


# TODO: Consolidate celestia and dymension queries (API breaking)
def get_celestia_host_zone(cast_types: bool = True) -> Dict[str, Any]:
    """
    Queries the celestia host zone from staketia

    Example response:
    {
        'chain_id': 'celestia',
        'native_token_denom': 'utia',
        'native_token_ibc_denom': 'ibc/BF3B4F53F3694B66E13C23107C84B6485BD2B96296BB7EC680EA77BBA75B4801',
        'transfer_channel_id': 'channel-162',
        'delegation_address': 'celestia1d6ntc7s8gs86tpdyn422vsqc6uaz9cejnxz5p5',
        'reward_address': 'celestia15up3hegy8zuqhy0p9m8luh0c984ptu2g5p4xpf',
        'deposit_address': 'stride1d6ntc7s8gs86tpdyn422vsqc6uaz9cejp8nc04',
        'redemption_address': 'stride15up3hegy8zuqhy0p9m8luh0c984ptu2gxqy20g',
        'claim_address': 'stride13nw9fm4ua8pwzmsx9kdrhefl4puz0tp7ge3gxd',
        'operator_address_on_stride': 'stride1ghhu67ttgmxrsyxljfl2tysyayswklvxs7pepw',
        'safe_address_on_stride': 'stride18p7xg4hj2u3zpk0v9gq68pjyuuua5wa387sjjc',
        'last_redemption_rate': '1.000000000000000000',
        'redemption_rate': '1.000000000000000000',
        'min_redemption_rate': '0.950000000000000000',
        'max_redemption_rate': '1.100000000000000000',
        'min_inner_redemption_rate': '0.950000000000000000',
        'max_inner_redemption_rate': '1.100000000000000000',
        'delegated_balance': '300000',
        'unbonding_period_seconds': '1814400',
        'halted': False
    }
    """
    url = f"{config.stride.api_endpoint}/{MULTISIG_HOST_ZONE_QUERY.format(module=STAKETIA)}"
    host_zone = request(url)["host_zone"]
    if cast_types:
        _cast_host_zone_fields(host_zone)
    return host_zone


def get_dymension_host_zone(cast_types: bool = True) -> Dict[str, Any]:
    """
    Queries the dymension host zone from stakedym

    Example response:
    {
        'chain_id': 'dymension',
        'native_token_denom': 'adym',
        'native_token_ibc_denom': 'ibc/E1C22332C083574F3418481359733BA8887D171E76C80AD9237422AEABB66018',
        'transfer_channel_id': 'channel-197',
        'delegation_address': 'dym1gl9j2hyyukqvlmzzcxl99mqfgu4y4frgzlv3zz',
        'reward_address': 'dym1ww3m6h5e3dk2musft9w8f2zu4rkuxgh6zwu0d0',
        'deposit_address': 'stride1e7j8d6sdq272fqe2jfxjpgcagn04j75w9695fj',
        'redemption_address': 'stride1jpsnc0ynufa2aheflj6mxzzzsu7nlwqk7ff69n',
        'claim_address': 'stride1q8juddwptg5yxyghh3n243pp4w8ctpvpmf6ras',
        'operator_address_on_stride': 'stride1ghhu67ttgmxrsyxljfl2tysyayswklvxs7pepw',
        'safe_address_on_stride': 'stride1sj8gyqeqecqhqu7em67hn2tjzhpkdf8wz5plh7',
        'last_redemption_rate': '1.000000000000000000',
        'redemption_rate': '1.000000000000000000',
        'min_redemption_rate': '0.950000000000000000',
        'max_redemption_rate': '1.100000000000000000',
        'min_inner_redemption_rate': '0.950000000000000000',
        'max_inner_redemption_rate': '1.100000000000000000',
        'delegated_balance': '300000',
        'unbonding_period_seconds': '1814400',
        'halted': False
    }
    """
    url = f"{config.stride.api_endpoint}/{MULTISIG_HOST_ZONE_QUERY.format(module=STAKEDYM)}"
    host_zone = request(url)["host_zone"]
    if cast_types:
        _cast_host_zone_fields(host_zone)
    return host_zone


def get_multisig_delegation_records(module: str, include_archived: bool = False) -> List[Dict]:
    """
    Queries the delegation records from staketia or stakedym
    Optionally include archive records

    Example response:
    [
        {
            'id': '515',
            'native_amount': '195100000',
            'status': 'DELEGATION_QUEUE',
            'tx_hash': ''
        },
        ...
    }
    """
    url = f"{config.stride.api_endpoint}/{MULTISIG_DELEGATION_RECORDS_QUERY.format(module=module)}"
    params = {"include_archived": include_archived}
    delegation_records = request(url, params=params)
    return delegation_records["delegation_records"]


def get_multisig_unbonding_records(module: str, include_archived: bool = False) -> List[Dict]:
    """
    Queries the celestia unbonding records from staketia or stakedym
    Optionally include archive records

    Args:
      module: str
      Custom multisig module name. e.g. `staketia` and `stakedym`

    Example response:
    [
        {
            'id': '1',
            'status': 'ACCUMULATING_REDEMPTIONS',
            'st_token_amount': '0',
            'native_amount': '0',
            'unbonding_completion_time_seconds': '0',
            'undelegation_tx_hash': '',
            'unbonded_token_sweep_tx_hash': '',
        },
        ...
    ]
    """
    url = f"{config.stride.api_endpoint}/{MULTISIG_UNBONDING_RECORDS_QUERY.format(module=module)}"
    params = {"include_archived": include_archived}
    unbonding_records = request(url, params=params)
    return unbonding_records["unbonding_records"]


def get_multisig_redemption_records(
    module: str,
    address: Optional[str] = None,
    unbonding_record_id: Optional[int] = None,
) -> List[Dict]:
    """
    Queries the celestia redemption records from staketia or stakedym
    Optionally include archive records

    Args:
      module: str
      Custom multisig module name. e.g. `staketia` and `stakedym`
    """
    params: Dict[str, Any] = {}
    if address:
        params["address"] = address
    if unbonding_record_id is not None:
        params["unbonding_record_id"] = unbonding_record_id

    url = f"{config.stride.api_endpoint}/{MULTISIG_REDEMPTION_RECORDS_QUERY.format(module=module)}"
    redemption_records = request(url, params=params)
    return redemption_records["redemption_record_responses"]


def get_rate_limits(**kwargs):
    """
    Queries all rate limits

    Returns:
      rate_limits: List[Dict]
      e.g. [{'path': {'denom': 'staevmos', 'channel_id': 'channel-9'},
            'quota': {'max_percent_send': '25',
             'max_percent_recv': '25',
             'duration_hours': '24'},
            'flow': {'inflow': '1065895546366311315936',
             'outflow': '1476888293332989296879000',
             'channel_value': '15104662663116448541290611'}}, ...]
    """
    endpoint = f"{config.stride.api_endpoint}/{RATE_LIMIT_QUERY}"
    host_zone = request(endpoint, **kwargs)["rate_limits"]
    return host_zone


def get_validators(
    api_endpoint: str = config.stride.api_endpoint,
) -> List[Dict[str, Any]]:
    """
    Queries the list of validators from a chain
    """
    url = f"{api_endpoint}/cosmos/staking/v1beta1/validators"
    return query_list_with_pagination(url, rel_key="validators")


def get_redemption_rate(token: str) -> float:
    """
    Queries the redemption rate for a particular token
    """
    js = get_host_zone_json(config.get_chain(ticker=token).id)
    return float(js["redemption_rate"])


def get_tvl_in_utokens(host_zone_id: str) -> float:
    """
    Queries the stride TVL for a given zone (denominated in the native token)
    """
    zone_info = config.get_chain(id=host_zone_id)
    js = get_host_zone_json(host_zone_id)
    delegation_key = "total_delegations"
    if delegation_key not in js:
        delegation_key = "delegated_balance"
    return int(js[delegation_key]) / pow(10, zone_info.denom_decimals)


def get_latest_block(rpc_endpoint: str = config.stride.rpc_endpoint) -> int:
    """
    Queries the latest block time for a given chain
    """
    url = f"{rpc_endpoint}/status"
    resp = request(url)
    return int(resp["result"]["sync_info"]["latest_block_height"])


def convert_cosmos_address(address: str, new_prefix: str) -> str:
    """
    Converts a Cosmos address to a different zone

    e.g. convert_cosmos_address("stride1am99pcvynqqhyrwqfvfmnvxjk96rn46le9j65c", "osmo")
         would return "osmo1am99pcvynqqhyrwqfvfmnvxjk96rn46lj4pkkx"
    """
    _, data = bech32.bech32_decode(address)
    if data is None:
        raise ValueError("invalid address")
    return bech32.bech32_encode(new_prefix, cast(List[int], data))


def get_balances(
    address: str,
    block_height: int = 0,
    api_endpoint: str = config.stride.library_api,
    cache_response: bool = False,
) -> Dict[str, int]:
    """
    Returns the balance of the given address across all tokens,
    returned as a dictionary of token -> balance
    """
    url = f"{api_endpoint}/{ACCOUNT_BALANCE_QUERY.format(address=address)}"
    response = request(url, block_height=block_height, cache_response=cache_response)
    return {balance["denom"]: int(balance["amount"]) for balance in response["balances"]}


def get_balance(
    address: str,
    denom: str,
    block_height: int = 0,
    api_endpoint: str = config.stride.library_api,
    cache_response: bool = False,
) -> int:
    """
    Returns the balance for a given address and token
    """
    url = f"{api_endpoint}/{ACCOUNT_BALANCE_QUERY.format(address=address)}/by_denom"
    params = {"denom": denom}
    response = request(url, block_height=block_height, params=params, cache_response=cache_response)
    return int(response["balance"]["amount"])


def get_supply(
    denom: str,
    block_height: int = 0,
    api_endpoint: str = config.stride.api_endpoint,
    cache_response: bool = False,
) -> int:
    """
    Returns the total token supply of a given token
    """
    url = f"{api_endpoint}/{SUPPLY_QUERY}"
    params = {"denom": denom}
    resp = request(url, block_height=block_height, params=params, cache_response=cache_response)
    return int(resp["amount"]["amount"])


@lru_cache
def get_block_time(height: int, rpc_endpoint: str = config.stride.library_rpc) -> datetime.datetime:
    """
    Returns the timestamp of the given block height on a chain
    """
    url = f"{rpc_endpoint}/block?height={height}"
    resp = request(url)
    block_time = resp["result"]["block"]["header"]["time"]
    block_datetime = dateutil.parser.parse(block_time).replace(tzinfo=None)
    return block_datetime


@lru_cache
def get_icns_name(address: str) -> str:
    """
    Returns the ICNS name for the given Cosmos-SDK address, if it exists

    e.g. get_icns_name("stride1am99pcvynqqhyrwqfvfmnvxjk96rn46le9j65c") = "shellvish"
    """
    icns_endpoint = (
        f"{config.host_zones.osmosis.api_endpoint}/cosmwasm/wasm/v1/contract"
        "/osmo1xk0s8xgktn9x5vwcgtjdxqzadg88fgn33p8u9cnpdxwemvxscvast52cdd/smart/"
    )
    query = '{"primary_name":{"address":"ADDRESS"}}'.replace("ADDRESS", address)
    # encode the query string and URL-encode it
    base64_str = str(base64.b64encode(query.encode("utf-8")))[2:-1]
    icns_endpoint += base64_str
    time.sleep(0.01)  # QUESTION: What's this sleep for?
    resp = request(icns_endpoint)
    return resp["data"]["name"]


def get_account_info(
    address: str,
    api_endpoint: str = config.stride.api_endpoint,
):
    """
    Returns the account information for a given address (including the sequence number)

     {'account':
         {'@type': '/cosmos.auth.v1beta1.BaseAccount',
          'address': 'stride1am99pcvynqqhyrwqfvfmnvxjk96rn46le9j65c',
          'pub_key': {'@type': '/cosmos.crypto.secp256k1.PubKey',
                      'key': 'A138uH3qwMpMbtRnvtuHgJMO6Cq+9iGlFkGUTYpVRQ9J'},
      'account_number': '90',
      'sequence': '553'}}
    """
    url = f"{api_endpoint}/{ACCOUNT_QUERY.format(address=address)}"
    return request(url)


def get_txs(event_filters: List[str], api_endpoint: str = config.stride.api_endpoint, limit=None) -> Dict:
    """
    Queries the txs endpoint with event filters
    Event filters are of the form `{event_type}.{event_attribute}={attribute_value}`
    Note: This only returns more recent txs that haven't already been pruned from the node

    E.g. To query for IBC transfer sent from a given address, you could use the filter:
         "ibc_transfer.sender='strideXXX'"

    The returned response structure returns list of txs and tx_responses where the indicies
    line up between the two arrays
    {
        "txs": [...],
        "tx_responses": [...]
    }
    """
    if len(event_filters) == 0:
        raise ValueError("At least one event filter is required when querying txs")

    url = f"{api_endpoint}/{TXS_QUERY}"
    params: List[Tuple[str, str]] = [("events", event_filter) for event_filter in event_filters]
    if limit is not None:
        params.append(('limit', limit))
    txs = request(url, params=params)

    return txs


# TODO: Rename to be more specific with address/sequence account query
def get_tx_info(
    address: str,
    sequence: Union[str, int],
    api_endpoint: str = config.stride.api_endpoint,
) -> Dict:
    """
    Returns the tx info for a given address and sequence number

    Response format:
     {'txs': [...]}
    """
    event_filter = TX_BY_ACCOUNT_EVENT.format(address=address, sequence=sequence)
    return get_txs(event_filters=[event_filter], api_endpoint=api_endpoint)


def generate_vesting_account(
    start_time_in_local_tz: str,
    total_tokens: int,
    seconds_in_period: int = 3600,
    number_of_days: int = 30,
    output_file: str = "vesting_account.json",
) -> str:
    """
    This function will generate a vesting account for the given number of days.
    It will start on the given start date (inputted as "YYYY-MM-DD HH:MM" in ET),
    and distribute the given number of ustrd tokens over the specified number of days.

    The vested tokens will be distributed over the specified number of days, with the period
    length being the specified number of seconds.

    The output is a JSON object that can be used to create a vesting account on the Stride chain.
    """
    timezone = pytz.timezone(config.TIMEZONE)
    start_time = timezone.localize(datetime.datetime.strptime(start_time_in_local_tz, "%Y-%m-%d %H:%M"))
    start_time = start_time.astimezone(pytz.utc)
    start_time = int(start_time.timestamp())

    out = '{ "start_time": ' + str(start_time) + ',\n  "periods":[\n'
    num_periods = int(number_of_days * 24 * 60 * 60) // seconds_in_period
    tokens_per_period = int(total_tokens / num_periods)
    for i in range(num_periods):
        out += "    {\n"
        out += f'    "coins": "{tokens_per_period}ustrd",\n'  # noqa: E231
        out += f'    "length_seconds":{seconds_in_period}\n'  # noqa: E231
        out += "  }"
        if i != num_periods - 1:
            out += ","
        out += "\n"
    out += "]}"
    with open(output_file, "w") as f:
        f.write(out)
    return out


def get_block_height_in_past(
    time_in_past: datetime.timedelta = datetime.timedelta(hours=24),
    max_acceptable_error_seconds: int = 60 * 5,
    seconds_per_block: int = 6,
    prev_time: Optional[str] = None,
    verbose: bool = False,
    rpc_endpoint: str = config.stride.library_rpc,
) -> int:
    """
    Gets the block height at a specified time by binary searching at different heights

    Args:
        time_in_past: target time to search for
        max_acceptable_error_seconds: max time delta before the height is considered find
        seconds_per_block: block time to use for the estimation start
        prev_time: Optional time to start the search at (instead of using time_in_past)

    Returns:
        The block height at the specified time
    """
    latest_block = get_latest_block(rpc_endpoint=rpc_endpoint)

    # set parameters so we can search for the block height
    blocks_per_day = (24 * 60 * 60) // seconds_per_block
    if prev_time is not None:
        if type(prev_time) is str:
            prev_time: datetime.datetime = pd.to_datetime(prev_time)  # type: ignore
        ts = (datetime.datetime.utcnow() - cast(datetime.datetime, prev_time)).total_seconds()
        num_days_back = ts / (60 * 60 * 24)
        time_in_past = datetime.timedelta(seconds=ts)
    else:
        num_days_back = time_in_past.total_seconds() / (60 * 60 * 24)
    blocks_in_past = int(num_days_back * blocks_per_day)
    time_estimate_error = float(100000)

    current_time = datetime.datetime.utcnow()

    # do an iterative search to find the block
    while abs(time_estimate_error) > max_acceptable_error_seconds:
        backwards_looking_height = latest_block - blocks_in_past
        backwards_looking_time = get_block_time(backwards_looking_height, rpc_endpoint=rpc_endpoint)
        time_estimate_error = (current_time - backwards_looking_time - time_in_past).total_seconds()
        error_in_blocks = time_estimate_error / seconds_per_block
        blocks_in_past -= int(error_in_blocks)
        if verbose:
            print("\tEstimated block: {}".format(backwards_looking_height))
            print("\tEstimated time: {}".format(backwards_looking_time))
            print("\tError in blocks: {}".format(error_in_blocks))
            print("\tTotal Seconds: {}".format(time_estimate_error))
            print("\t-------------------------")
    block_last_day = latest_block - blocks_in_past
    return block_last_day


def get_block_height_one_day_ago(verbose: bool = False) -> int:
    """
    Get the block height from 1 day ago
    """
    return get_block_height_in_past(datetime.timedelta(hours=24), verbose=verbose)


def get_sttoken_apr(token: str) -> Optional[float]:
    """
    Gets the APR of an stToken by querying upstash
        e.g. get_sttoken_apr('ATOM') will return roughly 0.19
    """
    apr = stride_upstash.get("STTOKEN_APR_" + token.upper(), db_name="public")
    if apr is None:
        raise ValueError("sttoken apr not found")
    return float(cast(str, apr))


def get_delegated_tokens_on_address(
    delegator_address: str,
    api_endpoint: str = config.stride.api_endpoint,
) -> Dict[str, int]:
    """
    Returns a dict mapping from "validator_address" to "num tokens delegated", given a delegator address

    Raw response example (stake_endpoint)
    {
      "delegation_responses": [
        {"delegation": {
            "delegator_address": "cosmos10...28",
            "validator_address": "cosmosvaloper1p..r2qs",
            "shares":"1.180957009445999997"},
            "balance":{"denom":"uatom","amount":"1"}
        }, ...],
      "pagination": {...}
    }

    Returns
      e.g. {'valoper1': 10, 'valoper2': 20}
    """
    stake_endpoint = f"{api_endpoint}/{ACCOUNT_DELEGATIONS_QUERY.format(delegator_address=delegator_address)}"
    host_zone_balance = query_list_with_pagination(stake_endpoint, rel_key="delegation_responses")
    stake_amounts: Dict[str, int] = {}
    for hzb in host_zone_balance:
        stake_amounts[hzb["delegation"]["validator_address"]] = int(hzb["balance"]["amount"])
    return stake_amounts


def get_unbonding_tokens_on_address(
    delegator_address: str,
    api_endpoint: str = config.stride.api_endpoint,
) -> Dict[str, int]:
    """
    Returns a dict mapping from "validator_address" to "num tokens delegated", given a delegator address

    Raw response example (unbonding_endpoint)
    {
      "unbonding_responses": [
        {
          "delegator_address": "cosmos10...28",
          "validator_address": "cosmosvaloper1d...h9",
          "entries": [
            {
              "creation_height": "18749801",
              "completion_time": "2024-02-06T19:00:28.676639972Z",
              "initial_balance": "3727000742",
              "balance": "3727000742",
              "unbonding_id": "334505",
              "unbonding_on_hold_ref_count": "1"
            }
          ]
        }, ...],
      "pagination": {...}
    }

    Returns
      e.g. {'valoper1': 10, 'valoper2': 20}
    """
    unbonding_endpoint = f"{api_endpoint}/{ACCOUNT_UNBONDINGS_QUERY.format(delegator_address=delegator_address)}"
    unbondings = query_list_with_pagination(unbonding_endpoint, rel_key="unbonding_responses")
    unbonding_amounts: Dict[str, int] = {}
    for unbonding in unbondings:
        unbonding_amounts[unbonding["validator_address"]] = sum(
            int(entry["initial_balance"]) for entry in unbonding["entries"]
        )
    return unbonding_amounts


def get_host_zone_delegations(host_zone_id: str, ground_truth_included: bool = True) -> pd.DataFrame:
    """
    Given a host zone id, returns a Dataframe of validator delegations.

    If `ground_truth_included=True`, then will also return the "true" delegations
    on the host zone delegaiton account.
    """
    host_zone = get_host_zone_json(host_zone_id)
    vdf = pd.DataFrame(host_zone["validators"])
    int_cols = [
        "weight",
        "delegation",
        "slash_query_progress_tracker",
        "slash_query_checkpoint",
        "shares_to_tokens_rate",
    ]
    for c in int_cols:
        vdf[c] = vdf[c].astype(float)
    vdf = vdf[
        [
            "name",
            "address",
            "weight",
            "delegation",
            "slash_query_in_progress",
            "slash_query_progress_tracker",
            "shares_to_tokens_rate",
        ]
    ]
    # get delegation on the host zone, if relevant
    if ground_truth_included:
        host_zone_delegation_account = host_zone["delegation_ica_address"]
        lcd_endpoint = config.get_chain(id=host_zone_id).api_endpoint
        stake_endpoint = f"{lcd_endpoint}/cosmos/staking/v1beta1/delegations/{host_zone_delegation_account}"
        host_zone_balance = request(stake_endpoint)["delegation_responses"]
        stake_amounts = {}
        for hzb in host_zone_balance:
            stake_amounts[hzb["delegation"]["validator_address"]] = float(hzb["balance"]["amount"])
        stake_amounts = pd.Series(stake_amounts)
        vdf["ground_delegation"] = (vdf["address"].map(stake_amounts)).fillna(0)
        float_cols = ["weight", "delegation", "ground_delegation"]
        for c in float_cols:
            vdf[c] = vdf[c].astype(float)
        filtered_vdf = vdf[(vdf["ground_delegation"] > 0) | (vdf["delegation"] > 0) | (vdf["weight"] > 0)]
        vdf = filtered_vdf
    return vdf


def get_epochs() -> List[Dict]:
    """
    Returns all the epochs on stride

    Example response:
    {
        {
            'identifier': 'day',
            'start_time': '2022-09-04T19:00:00.451745Z',
            'duration': '86400s',
            'current_epoch': '515',
            'current_epoch_start_time': '2024-01-31T19:00:00.451745Z',
            'epoch_counting_started': True,
            'current_epoch_start_height': '7483499'
        },
        ...
    }
    """
    url = f"{config.stride.api_endpoint}/{EPOCHS_QUERY}"
    epochs = request(url)
    return epochs["epochs"]


def get_day_epoch() -> int:
    """
    Get the day epoch from the stride-labs/stride/epochs endpoint
    """
    epochs_request = f"{config.stride.api_endpoint}/Stridelabs/stride/epochs"
    epochs = request(epochs_request)["epochs"]
    epochs_df = pd.DataFrame(epochs)
    day_epoch = int(epochs_df[epochs_df["identifier"] == "day"]["current_epoch"].values[0])
    return day_epoch


def query_wasm_contract(contract_address: str, query_msg: Dict, api_endpoint: str, block_height: int = 0) -> Dict:
    """
    Queries a cosmowasm contract address with the provided query message
    Response structure is dependent on the particular query
    """
    query_msg_string = json.dumps(query_msg)
    query_msg_encoded = base64.b64encode(query_msg_string.encode("utf-8")).decode("utf-8")

    query_path = COSMWASM_CONTRACT_QUERY.format(contract_address=contract_address, query=query_msg_encoded)
    data = request(f"{api_endpoint}/{query_path}", block_height=block_height)

    return data["data"]


def get_module_accounts(api_endpoint: str = config.stride.api_endpoint) -> List[Dict]:
    """
    Queries the list of all module accounts

    Returns a list of accounts like so:
    [
        {
            "@type": "/cosmos.auth.v1beta1.ModuleAccount",
            "base_account": {
                "address": "stride1fl48vsnmsdzcv85q5d2q4z5ajdha8yu3ksfndm",
                "pub_key": null,
                "account_number": "75",
                "sequence": "0"
            },
            "name": "bonded_tokens_pool",
        }
        ...
    """
    return request(f"{api_endpoint}/{MODULE_ACCOUNTS_QUERY}")["accounts"]


def get_empirical_annual_fees(ticker: str) -> float:
    """
    Returns the empirical annual fee, in dollars, that Stride collects for a given stToken.

    For example:
    get_empirical_annual_fees("ATOM") == 1005994.0745893999
    """
    empirical_dollar_fees = (
        stride_upstash.get("sheet_STRD_STAKING_ST{}_DOLLARS".format(ticker.upper()), db_name="frontend") or "0"
    )
    return float(cast(str, empirical_dollar_fees))
