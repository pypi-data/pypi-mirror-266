import typer

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

app = AsyncTyper(help="Users in the Validio platform")


@app.async_command(help="Get users")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
) -> None:
    vc, cfg = await get_client_and_config(config_dir)

    if identifier is not None:
        users = [
            await vc.get_user_by_resource_name(
                resource_name=identifier,
                resource_namespace=get_namespace(namespace, cfg),
            )
        ]
    else:
        users = await vc.get_users()

    if output_format == OutputFormat.JSON:
        return output_json(users, identifier)

    return output_text(
        users,
        fields={
            "name": OutputSettings(attribute_name="resource_name"),
            "role": None,
            "status": None,
            "identities": OutputSettings(reformat=lambda x: len(x)),
            "age": OutputSettings(attribute_name="created_at"),
        },
    )


if __name__ == "__main__":
    typer.run(app())
