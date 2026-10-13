"""Stage: sparse reconstruction → trained 3D Gaussian splat model."""
from __future__ import annotations

import logging

from gsforge.pipeline.context import PipelineContext
from gsforge.pipeline.registry import register
from gsforge.train.trainer import GaussianTrainer

log = logging.getLogger(__name__)


@register("train")
class TrainStage:
    name = "train"
    requires = ("sparse_dir", "images_dir")
    produces = ("checkpoint",)

    def run(self, ctx: PipelineContext) -> None:
        sparse_dir = ctx.require("sparse_dir")
        images_dir = ctx.require("images_dir")
        trainer = GaussianTrainer(
            cfg=ctx.cfg.train,
            sparse_dir=sparse_dir,
            images_dir=images_dir,
            out_dir=ctx.work_dir / "train",
        )
        ckpt = trainer.fit()
        ctx.mark("checkpoint", ckpt)
        ctx.metrics["train.psnr"] = trainer.last_psnr
        ctx.metrics["train.gaussians"] = float(trainer.last_num_gaussians)