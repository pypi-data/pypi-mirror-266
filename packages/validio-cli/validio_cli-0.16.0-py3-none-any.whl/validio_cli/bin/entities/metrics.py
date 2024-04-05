from datetime import datetime, timedelta

import typer
from validio_sdk.graphql_client.input_types import (
    TimeRangeInput,
    ValidatorSegmentMetricsInput,
)

from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    get_client_and_config,
    output_json,
    output_text,
)
from validio_cli.bin.entities import validators
from validio_cli.bin.entities.incidents import calculate_bound, calculate_operator

app = AsyncTyper(help="Metrics and incidents from validators")


@app.async_command(help="List all metrics")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    ended_before: datetime = typer.Option(
        datetime.utcnow(),
        help="Data seen before this timestamp",
    ),
    ended_after: datetime = typer.Option(
        (datetime.utcnow() - timedelta(hours=1)),
        help="Data seen after this timestamp",
    ),
    validator: str = typer.Option(..., help="Validator to fetch metrics for"),
    segment: str = typer.Option(..., help="Segment to fetch metrics for"),
) -> None:
    vc, cfg = await get_client_and_config(config_dir)

    if validator is not None:
        validator_id = await validators.get_validator_id(vc, cfg, validator, namespace)
        if validator_id is None:
            return None

    metrics = await vc.get_validator_segment_metrics(
        ValidatorSegmentMetricsInput(
            validator_id=validator_id,
            segment_id=segment,
            time_range=TimeRangeInput(
                start=ended_after,
                end=ended_before,
            ),
        )
    )

    if output_format == OutputFormat.JSON:
        return output_json(metrics)

    return output_text(
        metrics.values,
        fields={
            "operator": OutputSettings(
                pass_full_object=True,
                reformat=calculate_operator,
            ),
            "bound": OutputSettings(
                pass_full_object=True,
                reformat=calculate_bound,
            ),
            "value": None,
            "is_incident": None,
            "age": OutputSettings(
                attribute_name="end_time",
            ),
        },
    )


if __name__ == "__main__":
    typer.run(app())
