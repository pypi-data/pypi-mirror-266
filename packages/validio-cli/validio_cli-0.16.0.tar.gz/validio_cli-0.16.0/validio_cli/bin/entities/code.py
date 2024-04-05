import os
import pathlib
import sys
from collections.abc import Mapping
from enum import Enum
from typing import Any

import classdiff  # type: ignore
import typer
from validio_sdk import ValidioError
from validio_sdk.code import _import as code_import
from validio_sdk.code import apply as code_apply
from validio_sdk.code import plan as code_plan
from validio_sdk.code import scaffold
from validio_sdk.resource._diff import DiffContext, GraphDiff, ResourceUpdate
from validio_sdk.resource._resource import Resource
from validio_sdk.resource._util import SourceSchemaReinference
from validio_sdk.validio_client import ValidioAPIClient

from validio_cli import AsyncTyper, ConfigDir, Namespace, get_client_and_config
from validio_cli.bin.entities.resources import do_move
from validio_cli.components import proceed_with_operation

app = AsyncTyper(help="Plan or apply your configuration")


class DiffOutput(str, Enum):
    """Available output formats for the CLI"""

    FULL = "full"
    CHANGES = "changes"
    NONE = "none"


directory_option = typer.Option(
    "",
    help=(
        "The location to place the generated project; "
        "Defaults to the current directory if not specified"
    ),
)

no_capture_option: bool = typer.Option(
    False,
    help=(
        "By default, the code program's stdout output is hidden; "
        "enable this parameter to recover the output"
    ),
)

show_schema_option = typer.Option(
    False, help="Show the JTD schema in the plan output for Sources"
)

diff_option = typer.Option(
    DiffOutput.CHANGES.value,
    "--diff",
    help="Show only the changed lines (added, removed, or modified)",
)

color_option = typer.Option(
    not os.environ.get("NO_COLOR", False),
    help="Enable colored output",
)

destroy_option = typer.Option(
    False, help="Deletes all resources associated with the project"
)

show_secrets_option = typer.Option(
    False,
    help=(
        "By default, secret values within credentials are not shown; "
        "enable this parameter to show the values"
    ),
)

update_schema_option = typer.Option(
    None,
    help=(
        "Specify a Source name to update its schema. This checks the upstream data"
        " source for any schema changes before planning. You can use"
        " --update-schema src1 --update-schema src2 to specify multiple Sources."
    ),
)

update_all_schemas_option = typer.Option(
    False,
    help=(
        "Similar to --update-schema. Checks for schema "
        "updates for all Sources before planning"
    ),
)


@app.command(help="Initialize a new IaC project")
def init(
    directory: str = directory_option,
    force: bool = typer.Option(
        False, help="Forces project files to be generated in a non-empty directory"
    ),
    namespace: str = Namespace(
        "dev", help="A unique name to associate resources managed by the project"
    ),
) -> None:
    dir_path = directory_or_default(directory)

    scaffold._new_project(namespace, dir_path, force)


@app.async_command(help="Show changes to resources from an IaC configuration")
async def plan(
    directory: str = directory_option,
    no_capture: bool = no_capture_option,
    config_dir: str = ConfigDir,
    update_schema: list[str] = update_schema_option,
    update_all_schemas: bool = update_all_schemas_option,
    show_schema: bool = show_schema_option,
    diff_output: DiffOutput = diff_option,
    destroy: bool = destroy_option,
    show_secrets: bool = show_secrets_option,
    color: bool = color_option,
) -> None:
    dir_path = directory_or_default(directory)
    client, _ = await get_client_and_config(config_dir)

    schema_reinference = create_source_schema_reinference(
        update_schema, update_all_schemas
    )

    namespace = get_namespace(dir_path)
    await _plan(
        namespace=namespace,
        client=client,
        directory=dir_path,
        schema_reinference=schema_reinference,
        destroy=destroy,
        no_capture=no_capture,
        color=color,
        show_schema=show_schema,
        diff_output=diff_output,
        show_secrets=show_secrets,
    )


@app.async_command(help="Create or update resources from an IaC configuration")
async def apply(
    directory: str = directory_option,
    no_capture: bool = no_capture_option,
    auto_approve: bool = typer.Option(
        False, help="Automatically approve and perform plan operations"
    ),
    config_dir: str = ConfigDir,
    update_schema: list[str] = update_schema_option,
    update_all_schemas: bool = update_all_schemas_option,
    show_schema: bool = show_schema_option,
    diff_output: DiffOutput = diff_option,
    destroy: bool = destroy_option,
    show_secrets: bool = show_secrets_option,
    color: bool = color_option,
) -> None:
    dir_path = directory_or_default(directory)
    client, _ = await get_client_and_config(config_dir)

    schema_reinference = create_source_schema_reinference(
        update_schema, update_all_schemas
    )

    namespace = get_namespace(dir_path)
    diff, manifest_ctx = await _plan(
        namespace=namespace,
        client=client,
        directory=dir_path,
        schema_reinference=schema_reinference,
        destroy=destroy,
        no_capture=no_capture,
        color=color,
        show_schema=show_schema,
        diff_output=diff_output,
        show_secrets=show_secrets,
    )

    if diff.num_operations() == 0:
        return

    if not await proceed_with_operation(auto_approve):
        return

    print()
    print("Applying...")

    await code_apply.apply(
        namespace=namespace,
        client=client,
        ctx=manifest_ctx,
        diff=diff,
        show_secrets=show_secrets,
    )

    print(
        f"Apply complete! Resources: {diff.num_creates()} created, "
        f"{diff.num_updates()} updated, {diff.num_deletes()} deleted"
    )


@app.async_command(name="import", help="Import resources into the current project")
async def _import(
    directory: str = directory_option,
    no_capture: bool = no_capture_option,
    config_dir: str = ConfigDir,
    output: pathlib.Path = typer.Option(
        ...,
        "--output",
        "-o",
        help=(
            "The path to the file that will contain the generated resource declarations"
        ),
    ),
    import_namespace: str = typer.Option(
        None,
        "--import-namespace",
        help=(
            "If a file is specified, resources in that file will be moved."
            " Otherwise all resources in this namespace will be moved."
            " If providing file to move resources, this is a mandatory parameter"
        ),
    ),
    file: pathlib.Path = typer.Option(
        None,
        "--file",
        "-f",
        help=(
            "Path to a JSON-encoded file containing a list of resource to be"
            " moved into the current project before generating resource declarations."
            " If provided, then --import-namespace must be specified"
        ),
    ),
    auto_approve: bool = typer.Option(
        False, help="Automatically approve and perform the import operation"
    ),
) -> None:
    if file is not None and import_namespace is None:
        raise ValidioError(
            "--import-namespace must be provided if -f is provided and vice versa"
        )

    dir_path = directory_or_default(directory)
    client, _ = await get_client_and_config(config_dir)

    namespace = get_namespace(dir_path)

    if import_namespace:
        num_moved_resources = await do_move(
            client=client,
            namespace=import_namespace,
            target_namespace=namespace,
            file=file,
            auto_approve=auto_approve,
        )
        if num_moved_resources is None:
            return

        if num_moved_resources > 0:
            print(f"Moved {num_moved_resources} resources")

    diff, manifest_ctx = await _plan(
        namespace=namespace,
        client=client,
        directory=dir_path,
        schema_reinference=create_source_schema_reinference([], False),
        destroy=False,
        color=False,
        no_capture=no_capture,
        show_schema=False,
        show_secrets=False,
        show_diff=False,
    )

    if diff.num_deletes() == 0:
        _print_no_changes()
        return

    s = await code_import._import(ctx=diff.to_delete)
    output.write_text(s)
    print(f"Generated file {output.absolute()}")


def get_namespace(directory: pathlib.Path) -> str:
    settings = scaffold._read_project_settings(directory)
    return settings.namespace


def directory_or_default(directory: str) -> pathlib.Path:
    return (pathlib.Path(directory) if directory else pathlib.Path.cwd()).absolute()


async def _plan(
    namespace: str,
    client: ValidioAPIClient,
    directory: pathlib.Path,
    schema_reinference: SourceSchemaReinference,
    destroy: bool,
    no_capture: bool,
    color: bool,
    show_schema: bool = False,
    diff_output: DiffOutput = DiffOutput.FULL,
    show_secrets: bool = False,
    show_diff: bool = True,
) -> tuple[GraphDiff, DiffContext]:
    (diff, manifest_ctx) = await code_plan.plan(
        namespace=namespace,
        client=client,
        directory=directory,
        schema_reinference=schema_reinference,
        destroy=destroy,
        no_capture=no_capture,
        show_secrets=show_secrets,
    )

    if show_diff:
        if diff.num_operations() == 0:
            _print_no_changes()
            return diff, manifest_ctx

        _show_resources_diff(
            diff=diff,
            show_schema=show_schema,
            show_secrets=show_secrets,
            escape=sys.stdout.isatty() and color,
            diff_output=diff_output,
        )

    return diff, manifest_ctx


def _show_resources_diff(
    diff: GraphDiff,
    show_schema: bool,
    show_secrets: bool,
    escape: bool,
    diff_output: DiffOutput,
) -> None:
    resource_types = DiffContext.fields()
    if diff.num_creates() > 0:
        for t in resource_types:
            _show_create_resource_diff(
                getattr(diff.to_create, t),
                show_schema,
                show_secrets,
                escape,
                diff_output,
            )

    if diff.num_deletes() > 0:
        for t in resource_types:
            _show_delete_resource_diff(
                getattr(diff.to_delete, t),
                show_schema,
                show_secrets,
                escape,
                diff_output,
            )

    if diff.num_updates() > 0:
        for t in resource_types:
            _show_update_resource_diff(
                resources=getattr(diff.to_update, t),
                show_schema=show_schema,
                show_secrets=show_secrets,
                color=escape,
                diff_output=diff_output,
            )

    print(
        "\n"
        f"Plan: {diff.num_creates()} to create, {diff.num_updates()} to update, "
        f"{diff.num_deletes()} to delete."
    )


def _show_create_resource_diff(
    resources: Mapping[str, Resource],
    show_schema: bool,
    show_secrets: bool,
    color: bool,
    diff_output: DiffOutput,
) -> None:
    for r in resources.values():
        class_key = r.__class__.__name__

        print(f"{class_key} '{r.name}' will be created")

        rewrites = _diff_field_rewrites(show_schema)
        value = code_plan._create_resource_diff_object(
            r, rewrites=rewrites, show_secrets=show_secrets
        )

        _show_diff(None, value, color, diff_output, class_key)


def _show_delete_resource_diff(
    resources: Mapping[str, Resource],
    show_schema: bool,
    show_secrets: bool,
    color: bool,
    diff_output: DiffOutput,
) -> None:
    for r in resources.values():
        class_key = r.__class__.__name__

        print(f"{class_key} '{r.name}' will be deleted")

        rewrites = _diff_field_rewrites(show_schema)
        value = code_plan._create_resource_diff_object(
            r, rewrites=rewrites, show_secrets=show_secrets
        )

        _show_diff(value, None, color, diff_output, class_key)


def _show_update_resource_diff(
    resources: Mapping[str, ResourceUpdate],
    show_schema: bool,
    show_secrets: bool,
    color: bool,
    diff_output: DiffOutput,
) -> None:
    for r in resources.values():
        class_key = r.manifest.__class__.__name__

        print(f"{class_key} '{r.manifest.name}' will be updated")

        rewrites = _diff_field_rewrites(show_schema)

        a_value = code_plan._create_resource_diff_object(
            r.manifest,
            show_secrets=show_secrets,
            rewrites=rewrites,
            secrets_changed=r.secrets_changed,
            is_manifest=True,
        )
        b_value = code_plan._create_resource_diff_object(
            r.server,
            show_secrets=show_secrets,
            rewrites=rewrites,
            secrets_changed=r.secrets_changed,
            is_manifest=False,
        )

        _show_diff(b_value, a_value, color, diff_output, class_key)


def _show_diff(
    current_value: Any,
    new_value: Any,
    color: bool,
    diff_output: DiffOutput,
    class_key: str | None = None,
) -> None:
    if diff_output == DiffOutput.NONE:
        return

    diff = classdiff.diff(
        current_value,
        new_value,
        no_color=not color,
        changes_only=diff_output == DiffOutput.CHANGES,
        object_name=class_key,
    )

    print(diff)

    # We keep track if any lines were printed at all (any changes or full
    # output) and if not we don't add a newline. This is to make it more
    # condensed and consistent with the DiffOutput.NONE output.
    if diff:
        print()


def _diff_field_rewrites(show_schema: bool) -> dict[str, Any]:
    return {} if show_schema else {"jtd_schema": "[NOT SHOWN]"}


def create_source_schema_reinference(
    schemas_to_update: list[str], update_all_schemas: bool
) -> SourceSchemaReinference:
    source_names = None
    if update_all_schemas:
        source_names = []
    elif len(schemas_to_update) > 0:
        source_names = schemas_to_update

    return SourceSchemaReinference(set(source_names) if source_names else None)


def _print_no_changes() -> None:
    print("No changes. The configuration is up-to-date!")


if __name__ == "__main__":
    app()
