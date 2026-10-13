"""Thin wrapper around the COLMAP CLI. Never uses shell=True."""
from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from gsforge.config import Config

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ColmapResult:
    sparse_dir: Path
    images_dir: Path
    registered_count: int


def _run(args: Sequence[str], cwd: Path) -> None:
    log.debug("colmap: %s", " ".join(args))
    proc = subprocess.run(
        list(args),
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"colmap exited {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )


def run_colmap(cfg: Config, images: list[Path], work: Path) -> ColmapResult:
    work.mkdir(parents=True, exist_ok=True)
    db = work / "database.db"
    sparse = work / "sparse"
    dense = work / "dense"
    sparse.mkdir(exist_ok=True)
    dense.mkdir(exist_ok=True)

    gpu = "1" if cfg.reconstruct.use_gpu else "0"

    _run(
        ["colmap", "feature_extractor",
         "--database_path", str(db),
         "--image_path", str(images[0].parent),
         "--ImageReader.single_camera", "1" if cfg.reconstruct.single_camera else "0",
         "--ImageReader.camera_model", cfg.reconstruct.camera_model,
         "--SiftExtraction.use_gpu", gpu],
        cwd=work,
    )
    _run(
        ["colmap", cfg.reconstruct.matcher + "_matcher" if cfg.reconstruct.matcher != "exhaustive"
         else "exhaustive_matcher",
         "--database_path", str(db),
         "--SiftMatching.use_gpu", gpu],
        cwd=work,
    )
    _run(
        ["colmap", "mapper",
         "--database_path", str(db),
         "--image_path", str(images[0].parent),
         "--output_path", str(sparse)],
        cwd=work,
    )

    models = sorted(sparse.iterdir())
    if not models:
        raise RuntimeError("colmap mapper produced no sparse models")
    best = max(models, key=lambda p: (p / "images.bin").stat().st_size)

    registered = 0
    images_bin = best / "images.bin"
    if images_bin.exists():
        # 64-byte header per image record in COLMAP's binary format.
        registered = max(0, (images_bin.stat().st_size - 8) // 64)

    return ColmapResult(
        sparse_dir=best,
        images_dir=images[0].parent,
        registered_count=registered,
    )