from typing import IO, Optional

import click

from anyscale.controllers.compute_config_controller import ComputeConfigController
from anyscale.util import validate_non_negative_arg
from anyscale.utils.entity_arg_utils import format_inputs_to_entity


@click.group(
    "compute-config",
    short_help="Manage compute configurations on Anyscale.",
    help="Manages compute configurations to define cloud resource types and limitations.",
)
def compute_config_cli() -> None:
    pass


@compute_config_cli.command(
    name="create",
    help=(
        "Creates a new compute config. This accepts a yaml that follows the schema defined "
        "at https://docs.anyscale.com/reference/python-sdk/models#createclustercomputeconfig"
    ),
)
@click.argument("compute-config-file", type=click.File("rb"), required=True)
@click.option(
    "--name",
    "-n",
    help="Name for the created compute config.",
    required=False,
    type=str,
)
def create_compute_config(compute_config_file: IO[bytes], name: Optional[str]) -> None:
    ComputeConfigController().create(compute_config_file, name)


@compute_config_cli.command(
    name="delete", help="Delete the specified compute config.", hidden=True
)
@click.argument("compute-config-name", type=str, required=False)
@click.option(
    "--name",
    "-n",
    help="Name of the compute config to delete.",
    required=False,
    type=str,
)
@click.option(
    "--cluster-compute-id",
    help="Deprecated. Use --compute-config-id instead. Id of the compute config to archive. Must be provided if a compute name is not given.",
    required=False,
    type=str,
)
@click.option(
    "--compute-config-id",
    "--id",
    help="Id of the compute config to delete. Must be provided if a compute name is not given.",
    required=False,
    type=str,
)
def delete_compute_config(
    compute_config_name: Optional[str],
    name: Optional[str],
    cluster_compute_id: Optional[str],
    compute_config_id: Optional[str],
) -> None:
    if compute_config_name is not None and name is not None:
        raise click.ClickException(
            "Please only provide one of [COMPUTE_CONFIG_NAME] or --name."
        )

    if compute_config_id and cluster_compute_id:
        raise click.ClickException(
            "Please only provide one of --compute-config-id or --cluster-compute-id."
        )

    ComputeConfigController().delete(compute_config_name or name, cluster_compute_id)


@compute_config_cli.command(
    name="archive", help="Archive the specified compute config.",
)
@click.argument("compute-config-name", type=str, required=False)
@click.option(
    "--name",
    "-n",
    help="Name of the compute config to archive.",
    required=False,
    type=str,
)
@click.option(
    "--cluster-compute-id",
    help="Deprecated. Use --compute-config-id instead. Id of the compute config to archive. Must be provided if a compute name is not given.",
    required=False,
    type=str,
)
@click.option(
    "--compute-config-id",
    "--id",
    help="Id of the compute config to archive. Must be provided if a compute name is not given.",
    required=False,
    type=str,
)
def archive_compute_config(
    compute_config_name: Optional[str],
    name: Optional[str],
    cluster_compute_id: Optional[str],
    compute_config_id: Optional[str],
) -> None:
    if compute_config_name is not None and name is not None:
        raise click.ClickException(
            "Please only provide one of [COMPUTE_CONFIG_NAME] or --name."
        )

    if compute_config_id and cluster_compute_id:
        raise click.ClickException(
            "Please only provide one of --compute-config-id or --cluster-compute-id."
        )

    entity = format_inputs_to_entity(
        compute_config_name or name, compute_config_id or cluster_compute_id
    )
    ComputeConfigController().archive(entity)


@compute_config_cli.command(
    name="list",
    help=(
        "List information about compute configs on Anyscale. By default only list "
        "compute configs you have created."
    ),
)
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    help="List information about the compute config with this name.",
)
@click.option(
    "--cluster-compute-id",
    required=False,
    default=None,
    help=(
        "Deprecated. Use --compute-config-id instead. List information about the compute config with this id."
    ),
)
@click.option(
    "--compute-config-id",
    "--id",
    required=False,
    default=None,
    help=("List information about the compute config with this id."),
)
@click.option(
    "--include-shared",
    is_flag=True,
    default=False,
    help="Include all compute configs you have access to.",
)
@click.option(
    "--max-items",
    required=False,
    default=20,
    type=int,
    help="Max items to show in list.",
    callback=validate_non_negative_arg,
)
def list(  # noqa: A001
    name: Optional[str],
    cluster_compute_id: Optional[str],
    compute_config_id: Optional[str],
    include_shared: bool,
    max_items: int,
) -> None:
    cluster_compute_controller = ComputeConfigController()

    if compute_config_id and cluster_compute_id:
        raise click.ClickException(
            "Please only provide one of --compute-config-id or --cluster-compute-id."
        )

    cluster_compute_controller.list(
        cluster_compute_name=name,
        cluster_compute_id=compute_config_id or cluster_compute_id,
        include_shared=include_shared,
        max_items=max_items,
    )


@compute_config_cli.command(
    name="get", help=("Get details about compute configuration."),
)
@click.argument("compute-config-name", required=False)
@click.option(
    "--cluster-compute-id",
    required=False,
    default=None,
    help=(
        "Deprecated. Use --compute-config-id instead. Get details about compute configuration by this id."
    ),
)
@click.option(
    "--compute-config-id",
    "--id",
    required=False,
    default=None,
    help=("Get details about compute configuration by this id."),
)
@click.option(
    "--include-archived",
    is_flag=True,
    help=("Include archived compute configurations."),
)
def get(
    compute_config_name: Optional[str],
    cluster_compute_id: Optional[str],
    compute_config_id: Optional[str],
    include_archived: bool,
) -> None:
    cluster_compute_controller = ComputeConfigController()

    if compute_config_id and cluster_compute_id:
        raise click.ClickException(
            "Please only provide one of --compute-config-id or --cluster-compute-id."
        )

    cluster_compute_controller.get(
        cluster_compute_name=compute_config_name,
        cluster_compute_id=compute_config_id or cluster_compute_id,
        include_archived=include_archived,
    )
