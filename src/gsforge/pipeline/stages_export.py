"""Stage: trained model → .ply / .splat files ready for any viewer."""
from __future__ import annotations

import logging

from gsforge.pipeline.context import PipelineContext
from gsforge.pipeline.registry import register
from gsforge.io.splat_export import export_all

log = logging.getLogger(__name__)


@register("export")
class ExportStage:
    name = "export"
    requires = ("checkpoint",)
    produces = ("exports",)

    def run(self, ctx: PipelineContext) -> None:
        ckpt = ctx.require("checkpoint")
        written = export_all(ckpt, ctx.output_dir, ctx.cfg.export)
        ctx.mark("exports", ctx.output_dir)
        ctx.metrics["export.files"] = float(len(written))
        for path in written:
            log.info("wrote %s", path)