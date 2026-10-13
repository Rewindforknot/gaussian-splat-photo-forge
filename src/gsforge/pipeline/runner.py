"""Pipeline runner. Resolves stages by name and executes them in order."""
from __future__ import annotations

import logging
from pathlib import Path

from gsforge.config import Config
from gsforge.pipeline import registry
from gsforge.pipeline.context import PipelineContext

# Import stage modules so they self-register.
from gsforge.pipeline import stages_reconstruct, stages_train, stages_export  # noqa: F401

log = logging.getLogger(__name__)

DEFAULT_ORDER = ("reconstruct", "train", "export")


class PipelineRunner:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.ctx = PipelineContext(cfg=cfg, work_dir=Path(cfg.project.output_dir) / "work")

    def _prepare(self) -> None:
        self.ctx.work_dir.mkdir(parents=True, exist_ok=True)
        self.ctx.output_dir.mkdir(parents=True, exist_ok=True)

    def run_one(self, name: str) -> None:
        self._prepare()
        stage = registry.get(name)
        log.info("running stage %s", name)
        stage.run(self.ctx)

    def run_all(self) -> None:
        self._prepare()
        for name in DEFAULT_ORDER:
            stage = registry.get(name)
            log.info("running stage %s", name)
            stage.run(self.ctx)
        log.info("pipeline complete → %s", self.ctx.output_dir)