import typer
from validio_sdk.config import ValidioConfig
from validio_sdk.graphql_client.input_types import ResourceFilter
from validio_sdk.validio_client import ValidioAPIClient

from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Identifier,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    _single_resource_if_specified,
    get_client_and_config,
    output_json,
    output_text,
)
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Credentials used for Sources")


@app.async_command(help="Get credentials")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
) -> None:
    vc, cfg = await get_client_and_config(config_dir)

    if identifier is not None and not identifier.startswith("CRD_"):
        credentials = [
            await vc.get_credential_by_resource_name(
                resource_name=identifier,
                resource_namespace=namespace,
            )
        ]
    else:
        credentials = await vc.list_credentials(  # type: ignore
            filter=ResourceFilter(resource_namespace=get_namespace(namespace, cfg))
        )

    # TODO(UI-2311): Fully support list/get/get_by_resource_name
    credentials = _single_resource_if_specified(credentials, identifier)

    if output_format == OutputFormat.JSON:
        return output_json(credentials, identifier)

    return output_text(
        credentials,
        fields={
            "name": OutputSettings(attribute_name="resource_name"),
            "type": OutputSettings.trimmed_upper_snake("typename__", "Credential"),
            "age": OutputSettings(attribute_name="created_at"),
        },
    )


async def get_credential_id(
    vc: ValidioAPIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "credential"
    prefix = "CRD_"

    if identifier is None:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    # TODO: UI-1957 - Get a single resource by name
    resolved_id = next(
        (
            credential.id
            for credential in await vc.list_credentials(
                filter=ResourceFilter(resource_namespace=get_namespace(namespace, cfg))
            )
            if credential.resource_name == identifier
        ),
        None,
    )

    if resolved_id is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    return resolved_id


if __name__ == "__main__":
    typer.run(app())
