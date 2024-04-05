from dataclasses import dataclass

import typer

from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Identifier,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    get_client_and_config,
    output_json,
    output_text,
)
from validio_cli.bin.entities import segmentations

app = AsyncTyper(help="Segments for a segmentation")


@app.async_command(help="Get segment")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
    max_fields: int = typer.Option(3, help="Maximum number of fields to show"),
) -> None:
    vc, cfg = await get_client_and_config(config_dir)

    segmentation_id = await segmentations.get_segmentation_id(
        vc, cfg, identifier, namespace
    )
    if segmentation_id is None:
        return None

    segments = await vc.segments(id=segmentation_id)

    if output_format == OutputFormat.JSON:
        return output_json(segments)

    @dataclass
    class SegmentOutput:
        id: str
        muted: bool
        field_and_value: str

    resources = []
    for segment in segments:
        field_and_value = []
        for f in segment.fields:
            field_and_value.append(f"{f.field}={f.value}")

        additional = ""
        if len(field_and_value) > max_fields:
            additional = f" and {len(field_and_value)-max_fields} more"
            field_and_value = field_and_value[:max_fields]

        resources.append(
            SegmentOutput(
                id=segment.id,
                muted=segment.muted,
                field_and_value=", ".join(field_and_value) + additional,
            )
        )

    return output_text(
        resources,
        fields={
            "id": None,
            "muted": None,
            "field_and_value": None,
        },
    )


if __name__ == "__main__":
    typer.run(app())
