"""Config loading + schema. TOML in, frozen pydantic model out."""
from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

try:
    import tomllib  # py3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


class ProjectCfg(BaseModel):
    name: str = "untitled-scene"
    output_dir: str = "outputs"


class InputCfg(BaseModel):
    image_dir: str = "photos"
    image_exts: list[str] = Field(default_factory=lambda: [".jpg", ".png"])
    max_image_dim: int = 2000
    blur_reject_threshold: float = 60.0


class ReconstructCfg(BaseModel):
    backend: Literal["colmap", "pycolmap", "glomap"] = "colmap"
    matcher: Literal["exhaustive", "vocab_tree", "sequential"] = "exhaustive"
    use_gpu: bool = True
    camera_model: str = "OPENCV"
    single_camera: bool = True
    min_registered_images: int = 12


class TrainCfg(BaseModel):
    iterations: int = 30_000
    sh_degree: int = 3
    densify_until_iter: int = 15_000
    densify_grad_threshold: float = 2e-4
    position_lr_init: float = 1.6e-4
    white_background: bool = False
    save_every: int = 5_000


class ExportCfg(BaseModel):
    formats: list[Literal["ply", "splat"]] = Field(default_factory=lambda: ["ply", "splat"])
    ply_compressed: bool = True
    splat_sh_degree: int = 3


class ViewerCfg(BaseModel):
    auto_open: bool = False
    host: str = "127.0.0.1"
    port: int = 8080


class Config(BaseModel):
    project: ProjectCfg = ProjectCfg()
    input: InputCfg = InputCfg()
    reconstruct: ReconstructCfg = ReconstructCfg()
    train: TrainCfg = TrainCfg()
    export: ExportCfg = ExportCfg()
    viewer: ViewerCfg = ViewerCfg()


def load_config(path: Optional[Path]) -> Config:
    if path is None:
        default = Path(__file__).resolve().parents[2] / "config" / "default.toml"
        if not default.exists():
            return Config()
        path = default
    with path.open("rb") as fh:
        raw = tomllib.load(fh)
    return Config.model_validate(raw)