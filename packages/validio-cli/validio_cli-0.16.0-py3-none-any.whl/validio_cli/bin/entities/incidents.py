from datetime import datetime, timedelta
from typing import Any

import typer
from validio_sdk import ValidioError
from validio_sdk.graphql_client import (
    GetSourceIncidentsSource,
    GetValidatorIncidentsValidator,
)
from validio_sdk.graphql_client.input_types import TimeRangeInput

from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    _format_relative_time,
    get_client_and_config,
    output_json,
    output_text,
)
from validio_cli.bin.entities import sources, validators

app = AsyncTyper(help="Incidents from validators")


@app.async_command(
    help="""List all incidents.

By default you will get incidents from the last hour. You can specify a time
range for when the incident occurred by specifying when the incident ended.

You can list incidents in different ways:

* Listing all incidents

* Listing all source incidents for a specific source with --source

* Listing all incidents for a specific validator with --validator

* Listing all incidents for a specific segment with --segment

* Listing all incidents for a specific validator and segment with --validator
and --segment together
"""
)
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    ended_before: datetime = typer.Option(
        datetime.utcnow(),
        help="The incident ended before this timestamp",
    ),
    ended_after: datetime = typer.Option(
        (datetime.utcnow() - timedelta(hours=1)),
        help="The incident ended after this timestamp",
    ),
    validator: str = typer.Option(None, help="Validator to fetch incidents for"),
    segment: str = typer.Option(None, help="Segment to fetch incidents for"),
    source: str = typer.Option(None, help="Source to fetch incidents for"),
) -> None:
    vc, cfg = await get_client_and_config(config_dir)

    if validator is not None:
        validator_id = await validators.get_validator_id(vc, cfg, validator, namespace)
        if validator_id is None:
            return None

    if source is not None:
        source_id = await sources.get_source_id(vc, cfg, source, namespace)
        if source_id is None:
            return None

    # TODO(UI-2006): These should all support namespace

    incidents: (None | GetValidatorIncidentsValidator | GetSourceIncidentsSource) = None

    if validator:
        incidents = await vc.get_validator_incidents(
            id=validator_id,
            range=TimeRangeInput(
                start=ended_after,
                end=ended_before,
            ),
            segment_id=segment,
        )
    elif source:
        incidents = await vc.get_source_incidents(
            id=source_id,
            range=TimeRangeInput(
                start=ended_after,
                end=ended_before,
            ),
        )
    else:
        raise ValidioError(
            "You need to specify one of --validator and/or --segment or --source"
        )

    if not incidents:
        return output_text(None, {})

    if output_format == OutputFormat.JSON:
        return output_json(incidents)

    return output_text(
        incidents.incidents,
        fields={
            "operator": OutputSettings(
                attribute_name="metric",
                reformat=calculate_operator,
            ),
            "bound": OutputSettings(
                attribute_name="metric",
                reformat=calculate_bound,
            ),
            "value": OutputSettings(
                attribute_name="metric",
                reformat=lambda x: x.value,
            ),
            "age": OutputSettings(
                attribute_name="metric",
                reformat=lambda x: _format_relative_time(x.end_time),
            ),
        },
    )


def calculate_operator(item: Any) -> str:
    type_ = item.typename__[len("ValidatorMetricWith") :]
    if type_ == "DynamicThreshold":
        operator = item.decision_bounds_type
    else:
        operator = item.operator

    return f"{type_}/{operator}"


def calculate_bound(item: Any) -> str:
    type_ = item.typename__[len("ValidatorMetricWith") :]
    if type_ == "DynamicThreshold":
        bound = f"{item.lower_bound:.2f} - {item.upper_bound:.2f}"
    elif type_ == "FixedThreshold":
        bound = item.bound
    else:
        bound = "-"

    return bound


if __name__ == "__main__":
    typer.run(app())
