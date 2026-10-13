"""Command-line entry point for gsforge."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from gsforge.config import load_config
from gsforge.pipeline.runner import PipelineRunner

app = typer.Typer(
    name="gsforge",
    help="Turn a folder of photos into a 3D Gaussian splat scene.",
    no_args_is_help=True,
)
console = Console()


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@app.command()
def run(
    image_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    output_dir: Path = typer.Option(Path("outputs"), "--out", "-o"),
    config: Optional[Path] = typer.Option(None, "--config", "-c"),
    stage: Optional[str] = typer.Option(
        None, "--stage", help="Run a single stage (reconstruct|train|export)."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Run the full photo → splat pipeline."""
    _setup_logging(verbose)
    cfg = load_config(config)
    cfg.input.image_dir = str(image_dir)
    cfg.project.output_dir = str(output_dir)
    runner = PipelineRunner(cfg)
    if stage:
        runner.run_one(stage)
    else:
        runner.run_all()


@app.command()
def validate(image_dir: Path = typer.Argument(..., exists=True, file_okay=False)) -> None:
    """Validate an image folder before a long pipeline run."""
    from gsforge.utils.image_scan import scan_images

    result = scan_images(image_dir)
    console.print(f"[bold]Found[/bold] {len(result.accepted)} usable images")
    if result.rejected:
        console.print(f"[yellow]Rejected[/yellow] {len(result.rejected)} frames (blur / corrupt)")
        for path, reason in result.rejected[:10]:
            console.print(f"  - {path.name}: {reason}")


if __name__ == "__main__":
    app()