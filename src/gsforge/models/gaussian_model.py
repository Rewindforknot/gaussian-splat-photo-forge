"""The actual Gaussian cloud: xyz, scale, rot, opacity, SH coefficients."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch


@dataclass
class GaussianData:
    xyz: torch.Tensor          # (N, 3)
    scales: torch.Tensor       # (N, 3) log-space
    rotations: torch.Tensor    # (N, 4) unit quaternion
    opacities: torch.Tensor    # (N, 1) logit-space
    sh_dc: torch.Tensor        # (N, 1, 3)
    sh_rest: torch.Tensor      # (N, K, 3) K = (sh_degree+1)^2 - 1


class GaussianModel:
    def __init__(self, data: GaussianData, device: torch.device) -> None:
        self.device = device
        self.data = data
        self.num_gaussians = data.xyz.shape[0]

    @classmethod
    def init_from_sparse(cls, sparse_dir: Path, sh_degree: int) -> GaussianData:
        pts_path = sparse_dir / "points3D.bin"
        if not pts_path.exists():
            raise FileNotFoundError(f"missing {pts_path}")
        xyz = _read_points3d_bin(pts_path).astype(np.float32)
        n = xyz.shape[0]
        k = (sh_degree + 1) ** 2 - 1
        return GaussianData(
            xyz=torch.from_numpy(xyz),
            scales=torch.full((n, 3), -3.0),
            rotations=torch.tensor([1.0, 0.0, 0.0, 0.0]).repeat(n, 1),
            opacities=torch.full((n, 1), 0.1),
            sh_dc=torch.zeros(n, 1, 3),
            sh_rest=torch.zeros(n, k, 3),
        )

    def build_optimizers(self, position_lr: float, iterations: int) -> dict[str, torch.optim.Adam]:
        return {
            "xyz": torch.optim.Adam([self.data.xyz], lr=position_lr),
            "scale": torch.optim.Adam([self.data.scales], lr=5e-3),
            "rot": torch.optim.Adam([self.data.rotations], lr=1e-3),
            "opacity": torch.optim.Adam([self.data.opacities], lr=5e-2),
            "sh": torch.optim.Adam([self.data.sh_dc, self.data.sh_rest], lr=2.5e-3),
        }

    def render(self, cam):  # pragma: no cover - delegates to CUDA rasterizer
        raise NotImplementedError("hook your rasterizer backend here")

    def loss(self, rendered: torch.Tensor, gt: torch.Tensor) -> torch.Tensor:
        l1 = torch.abs(rendered - gt).mean()
        ssim = _ssim(rendered, gt)
        return 0.8 * l1 + 0.2 * (1.0 - ssim)

    def psnr(self, rendered: torch.Tensor, gt: torch.Tensor) -> float:
        mse = torch.mean((rendered - gt) ** 2).item()
        return 10.0 * float(np.log10(1.0 / max(mse, 1e-12)))

    def densify_and_prune(self, grad_threshold: float, scene_extent: float) -> None:
        # Skeleton: real implementation grows+prunes based on view-space
        # gradients. Left as a hook for the CUDA rasterizer's accumulators.
        return

    def save_ply(self, path: Path) -> None:
        from gsforge.io.ply_writer import write_ply

        write_ply(
            path,
            xyz=self.data.xyz.detach().cpu().numpy(),
            scales=self.data.scales.detach().cpu().numpy(),
            rotations=self.data.rotations.detach().cpu().numpy(),
            opacities=self.data.opacities.detach().cpu().numpy(),
            sh_dc=self.data.sh_dc.detach().cpu().numpy(),
            sh_rest=self.data.sh_rest.detach().cpu().numpy(),
        )


def _read_points3d_bin(path: Path) -> np.ndarray:
    """Parse COLMAP points3D.bin. Layout: uint64 N, then fixed 43-byte records."""
    with path.open("rb") as fh:
        n = int.from_bytes(fh.read(8), "little")
        rec = 8 + 3 * 8 + 3 + 3 * 8 + 8  # id + xyz + rgb + err + track
        out = np.empty((n, 3), dtype=np.float64)
        for i in range(n):
            chunk = fh.read(rec)
            out[i] = np.frombuffer(chunk[8:32], dtype=np.float64)
    return out


def _ssim(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:  # pragma: no cover
    return torch.tensor(0.0, device=a.device)