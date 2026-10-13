"""Mutable context threaded through every pipeline stage."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from gsforge.config import Config


@dataclass
class PipelineContext:
    cfg: Config
    work_dir: Path
    artifacts: dict[str, Path] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)

    @property
    def output_dir(self) -> Path:
        return Path(self.cfg.project.output_dir)

    def mark(self, key: str, path: Path) -> None:
        self.artifacts[key] = path

    def require(self, key: str) -> Path:
        if key not in self.artifacts:
            raise KeyError(f"artifact {key!r} not produced yet")
        return self.artifacts[key]