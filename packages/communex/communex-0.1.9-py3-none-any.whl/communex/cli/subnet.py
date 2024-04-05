from typing import Any, Optional, cast

import typer
from rich.console import Console

from communex.balance import from_nano
from communex.compat.key import classic_load_key
from communex.errors import ChainTransactionError
from communex.misc import get_map_subnets_params
from communex.types import Ss58Address, SubnetParams

from .._common import make_client
from ._common import print_table_from_plain_dict

subnet_app = typer.Typer()


@subnet_app.command()
def list():
    """
    Gets subnets.
    """

    console = Console()
    client = make_client()

    with console.status("Getting subnets ..."):
        subnets = get_map_subnets_params(client)

    keys, values = subnets.keys(), subnets.values()
    subnets_with_netuids = [{"netuid": key, **value} for key, value in zip(keys, values)]

    subnet_stakes = client.query_map_total_stake()

    subnets_with_stakes = [{"stake": from_nano(subnet_stakes.get(netuid, 0))} for netuid in keys]
    subnets_with_stakes = [{**subnets_with_netuids[i], **subnets_with_stakes[i]}
                           for i in range(len(keys))]

    subnets_with_netuids = sorted(
        subnets_with_stakes, key=lambda x: x["emission"], reverse=True)

    for dict in subnets_with_netuids:
        print_table_from_plain_dict(dict, ["Params", "Values"], console)


@subnet_app.command()
def info(netuid: int):
    """
    Gets subnet info.
    """

    console = Console()
    client = make_client()

    with console.status(f"Getting subnet with netuid '{netuid}'..."):

        subnets = get_map_subnets_params(client)
        subnet = subnets.get(netuid, None)

    if subnet is None:
        raise ValueError("Subnet not found")

    general_subnet: dict[str, Any] = cast(dict[str, Any], subnet)
    print_table_from_plain_dict(general_subnet, ["Params", "Values"], console)


# TODO refactor (user does not need to specify all params)
@subnet_app.command()
def update(netuid: int,
           name: str,
           founder: str,
           founder_share: int,
           immunity_period: int,
           incentive_ratio: int,
           max_allowed_uids: int,
           max_allowed_weights: int,
           min_allowed_weights: int,
           max_stake: int,
           min_stake: int,
           tempo: int,
           trust_ratio: int,
           vote_mode: str,
           vote_threshold: int,
           key: str,
           max_weight_age: int,
           password: Optional[str] = None):
    """
    Updates a subnet.
    """

    console = Console()
    client = make_client()

    params: SubnetParams = {
        "name": name,
        "founder": Ss58Address(founder),
        "founder_share": founder_share,
        "immunity_period": immunity_period,
        "incentive_ratio": incentive_ratio,
        "max_allowed_uids": max_allowed_uids,
        "max_allowed_weights": max_allowed_weights,
        "min_allowed_weights": min_allowed_weights,
        "max_stake": max_stake,
        "min_stake": min_stake,
        "tempo": tempo,
        "trust_ratio": trust_ratio,
        "vote_mode": vote_mode,
        "vote_threshold": vote_threshold,
        "max_weight_age": max_weight_age,
    }

    resolved_key = classic_load_key(key)

    with console.status("Updating subnet ..."):
        response = (client.update_subnet(key=resolved_key, params=params, netuid=netuid))

        if response.is_success:
            console.print(f"Successfully updated subnet {name} with netuid {netuid}")
        else:
            raise ChainTransactionError(response.error_message)  # type: ignore
