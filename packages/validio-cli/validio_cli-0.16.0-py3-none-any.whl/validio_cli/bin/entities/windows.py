import typer
from camel_converter import to_snake
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
    _single_resource_if_specified,
    get_client_and_config,
    output_json,
    output_text,
)
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Windows used to group data for calculations")


@app.async_command(help="Get windows")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
    source: str = typer.Option(None, help="List Windows for this source (ID or name)"),
) -> None:
    vc, cfg = await get_client_and_config(config_dir)

    if identifier is not None and not identifier.startswith("WDW_"):
        windows = [
            await vc.get_window_by_resource_name(
                resource_name=identifier,
                resource_namespace=get_namespace(namespace, cfg),
            )
        ]
    else:
        windows = await vc.list_windows(  # type: ignore
            filter=ResourceFilter(resource_namespace=get_namespace(namespace, cfg))
        )

    windows = [
        window
        for window in windows
        if window is not None
        and validio_cli._resource_filter(window, ["source"], source)
    ]

    # TODO(UI-2311): Fully support list/get/get_by_resource_name
    windows = _single_resource_if_specified(windows, identifier)

    if output_format == OutputFormat.JSON:
        return output_json(windows, identifier)

    return output_text(
        windows,
        fields={
            "name": OutputSettings(attribute_name="resource_name"),
            "source": OutputSettings(reformat=lambda source: source.resource_name),
            "type": OutputSettings(
                attribute_name="typename__",
                reformat=lambda x: to_snake(
                    x.removesuffix("Window").removesuffix("Batch")
                ).upper(),
            ),
            "age": OutputSettings(attribute_name="created_at"),
        },
    )


async def get_window_id(
    vc: ValidioAPIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "window"
    prefix = "WDW_"

    if identifier is None:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await vc.get_window_by_resource_name(
        resource_name=identifier,
        resource_namespace=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    return resource.id


if __name__ == "__main__":
    typer.run(app())
