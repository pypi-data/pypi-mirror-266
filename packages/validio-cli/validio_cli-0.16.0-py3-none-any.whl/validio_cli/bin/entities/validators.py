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

app = AsyncTyper(help="Validators monitor the data from your sources")


@app.async_command(help="Get Validators")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
    source: str = typer.Option(
        None, help="List Validators for this Source (name or ID)"
    ),
    window: str = typer.Option(
        None, help="List Validators for this Window (name or ID)"
    ),
    segmentation: str = typer.Option(
        None, help="List Validators for this Segmentation (name or ID)"
    ),
) -> None:
    vc, cfg = await get_client_and_config(config_dir)

    validators: list[Any] = []

    if identifier is not None and identifier.startswith("MTR_"):
        validators.append(await vc.get_validator(id=identifier))
    elif identifier is not None:
        validators.append(
            await vc.get_validator_by_resource_name(
                resource_name=identifier,
                resource_namespace=get_namespace(namespace, cfg),
            )
        )
    elif source is None or not source.startswith("SRC_"):
        for s in await vc.list_sources(
            filter=ResourceFilter(resource_namespace=get_namespace(namespace, cfg))
        ):
            validators.extend(
                await vc.list_validators(
                    id=s.id,
                    filter=ResourceFilter(
                        resource_namespace=get_namespace(namespace, cfg)
                    ),
                ),
            )
    else:
        validators = await vc.list_validators(
            id=source,
            filter=ResourceFilter(resource_namespace=get_namespace(namespace, cfg)),
        )

    validators = [
        validator
        for validator in validators
        if validio_cli._resource_filter(validator, ["source_config", "source"], source)
        and validio_cli._resource_filter(validator, ["source_config", "window"], window)
        and validio_cli._resource_filter(
            validator, ["source_config", "segmentation"], segmentation
        )
    ]

    if output_format == OutputFormat.JSON:
        return output_json(validators, identifier)

    return output_text(
        validators,
        fields={
            "name": OutputSettings(attribute_name="resource_name"),
            "type": OutputSettings.trimmed_upper_snake("typename__", "Validator"),
            "age": OutputSettings(attribute_name="created_at"),
        },
    )


async def get_validator_id(
    vc: ValidioAPIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "validator"
    prefix = "MTR_"

    if identifier is None:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await vc.get_validator_by_resource_name(
        resource_name=identifier,
        resource_namespace=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    return resource.id


if __name__ == "__main__":
    app()
