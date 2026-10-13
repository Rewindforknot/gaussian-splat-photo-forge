"""Minimal 3DGS trainer. Wraps the reference rasterizer if available."""
from __future__ import annotations

import logging
from pathlib import Path

import torch

from gsforge.config import TrainCfg
from gsforge.models.gaussian_model import GaussianModel
from gsforge.models.camera import CameraBatch

log = logging.getLogger(__name__)


class GaussianTrainer:
    def __init__(
        self,
        cfg: TrainCfg,
        sparse_dir: Path,
        images_dir: Path,
        out_dir: Path,
    ) -> None:
        self.cfg = cfg
        self.sparse_dir = sparse_dir
        self.images_dir = images_dir
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.last_psnr = 0.0
        self.last_num_gaussians = 0

    def fit(self) -> Path:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        cameras = CameraBatch.from_colmap(self.sparse_dir, self.images_dir, device)
        points = GaussianModel.init_from_sparse(self.sparse_dir, sh_degree=self.cfg.sh_degree)
        model = GaussianModel(points, device=device)

        optimizers = model.build_optimizers(
            position_lr=self.cfg.position_lr_init,
            iterations=self.cfg.iterations,
        )

        for it in range(self.cfg.iterations):
            cam = cameras.sample()
            rendered, _ = model.render(cam)
            loss = model.loss(rendered, cam.gt_image)
            loss.backward()
            for opt in optimizers.values():
                opt.step()
                opt.zero_grad(set_to_none=True)
            if it < self.cfg.densify_until_iter:
                model.densify_and_prune(
                    grad_threshold=self.cfg.densify_grad_threshold,
                    scene_extent=cameras.scene_extent,
                )
            if it % self.cfg.save_every == 0:
                self.last_psnr = float(model.psnr(rendered, cam.gt_image))
                self.last_num_gaussians = model.num_gaussians
                log.info(
                    "iter %d  psnr %.2f  gaussians %d",
                    it, self.last_psnr, self.last_num_gaussians,
                )

        ckpt = self.out_dir / "point_cloud.ply"
        model.save_ply(ckpt)
        return ckpt