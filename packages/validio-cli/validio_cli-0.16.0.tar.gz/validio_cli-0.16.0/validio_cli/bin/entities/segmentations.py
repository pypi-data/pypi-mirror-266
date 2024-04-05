from typing import Any

import typer
from validio_sdk.config import ValidioConfig
from validio_sdk.graphql_client.input_types import ResourceFilter
from validio_sdk.validio_client import ValidioAPIClient

import validio_cli
from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Identifier,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    get_client_and_config,
    output_json,
    output_text,
)
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Grouping of data for validation")


@app.async_command(help="List all Segmentations")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
    source: str = typer.Option(
        None, help="List Segmentations for this Source (ID or name)"
    ),
) -> None:
    vc, cfg = await get_client_and_config(config_dir)

    segmentations: list[Any] = []

    if identifier is not None and identifier.startswith("SGM_"):
        segmentations = [await vc.get_segmentation(id=identifier)]
    elif identifier is not None:
        segmentations = [
            await vc.get_segmentation_by_resource_name(
                resource_name=identifier,
                resource_namespace=get_namespace(namespace, cfg),
            )
        ]
    else:
        segmentations = await vc.list_segmentations(
            filter=ResourceFilter(resource_namespace=get_namespace(namespace, cfg))
        )

    segmentations = [
        segmentation
        for segmentation in segmentations
        if segmentation is not None
        and validio_cli._resource_filter(segmentation, ["source"], source)
    ]

    if output_format == OutputFormat.JSON:
        return output_json(segmentations, identifier)

    return output_text(
        segmentations,
        fields={
            "name": OutputSettings(attribute_name="resource_name"),
            "source": OutputSettings(reformat=lambda source: source.resource_name),
            "age": OutputSettings(attribute_name="created_at"),
        },
    )


async def get_segmentation_id(
    vc: ValidioAPIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "segmentation"
    prefix = "SGM_"

    if identifier is None:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await vc.get_segmentation_by_resource_name(
        resource_name=identifier,
        resource_namespace=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    return resource.id


if __name__ == "__main__":
    typer.run(app())
