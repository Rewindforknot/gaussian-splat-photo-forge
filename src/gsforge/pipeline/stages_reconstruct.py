"""Stage: photo folder → sparse SfM reconstruction (COLMAP)."""
from __future__ import annotations

import logging

from gsforge.pipeline.context import PipelineContext
from gsforge.pipeline.registry import register
from gsforge.reconstruct.colmap_runner import run_colmap
from gsforge.utils.image_scan import scan_images

log = logging.getLogger(__name__)


@register("reconstruct")
class ReconstructStage:
    name = "reconstruct"
    requires: tuple[str, ...] = ()
    produces = ("sparse_dir", "images_dir")

    def run(self, ctx: PipelineContext) -> None:
        image_dir = ctx.cfg.input.image_dir
        scan = scan_images(image_dir)
        if len(scan.accepted) < ctx.cfg.reconstruct.min_registered_images:
            raise RuntimeError(
                f"only {len(scan.accepted)} usable images; need "
                f">= {ctx.cfg.reconstruct.min_registered_images}"
            )
        sparse = run_colmap(ctx.cfg, scan.accepted, ctx.work_dir / "colmap")
        ctx.mark("sparse_dir", sparse.sparse_dir)
        ctx.mark("images_dir", sparse.images_dir)
        ctx.metrics["images.registered"] = float(sparse.registered_count)