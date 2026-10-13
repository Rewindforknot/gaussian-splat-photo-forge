"""Camera batch loaded from a COLMAP sparse reconstruction."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch


@dataclass
class Camera:
    intrinsics: torch.Tensor   # (3, 3)
    extrinsics: torch.Tensor   # (4, 4) world → cam
    gt_image: torch.Tensor     # (H, W, 3) in [0, 1]
    width: int
    height: int


class CameraBatch:
    def __init__(self, cameras: list[Camera], scene_extent: float) -> None:
        self.cameras = cameras
        self.scene_extent = scene_extent

    @classmethod
    def from_colmap(cls, sparse_dir: Path, images_dir: Path, device: torch.device) -> "CameraBatch":
        if not (sparse_dir / "cameras.bin").exists():
            raise FileNotFoundError(f"no cameras.bin in {sparse_dir}")
        # Real loader parses cameras.bin + images.bin and pairs each pose
        # with its image from images_dir. Kept as a placeholder so the repo
        # ships without a hard dependency on the COLMAP binary format.
        return cls(cameras=[], scene_extent=1.0)

    def sample(self) -> Camera:
        if not self.cameras:
            raise RuntimeError("no cameras loaded; run reconstruct first")
        idx = torch.randint(0, len(self.cameras), (1,)).item()
        return self.cameras[idx]