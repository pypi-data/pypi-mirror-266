import typer
from camel_converter import to_snake
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

app = AsyncTyper(help="Notification rules for incidents")


@app.async_command(help="Get notification rules")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
) -> None:
    vc, cfg = await get_client_and_config(config_dir)

    if identifier is not None and not identifier.startswith("NRL_"):
        notification_rules = [
            await vc.get_notification_rule_by_resource_name(
                resource_name=identifier,
                resource_namespace=get_namespace(namespace, cfg),
            )
        ]
    else:
        notification_rules = await vc.get_notification_rules(  # type: ignore
            filter=ResourceFilter(resource_namespace=get_namespace(namespace, cfg))
        )

    # TODO(UI-2311): Fully support list/get/get_by_resource_name
    notification_rules = _single_resource_if_specified(notification_rules, identifier)

    if output_format == OutputFormat.JSON:
        return output_json(notification_rules, identifier)

    return output_text(
        notification_rules,
        fields={
            "name": OutputSettings(attribute_name="resource_name"),
            "channel": OutputSettings(reformat=lambda x: x.resource_name),
            "type": OutputSettings(
                attribute_name="channel",
                reformat=lambda x: to_snake(
                    x.typename__.removesuffix("Channel")
                ).upper(),
            ),
            "age": OutputSettings(attribute_name="created_at"),
        },
    )


async def get_notification_rule_id(
    vc: ValidioAPIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "notification rule"
    prefix = "NRL_"

    if identifier is None:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await vc.get_notification_rule_by_resource_name(
        resource_name=identifier,
        resource_namespace=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    return resource.id


if __name__ == "__main__":
    typer.run(app())
