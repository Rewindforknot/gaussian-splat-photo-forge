"""Write standard 3DGS-compatible binary PLY files."""
from __future__ import annotations

from pathlib import Path

import numpy as np

_MAGIC = b"ply\nformat binary_little_endian 1.0\n"


def write_ply(
    path: Path,
    *,
    xyz: np.ndarray,
    scales: np.ndarray,
    rotations: np.ndarray,
    opacities: np.ndarray,
    sh_dc: np.ndarray,
    sh_rest: np.ndarray,
) -> None:
    n = xyz.shape[0]
    k = sh_rest.shape[1]
    path.parent.mkdir(parents=True, exist_ok=True)

    header = bytearray(_MAGIC)
    header += f"element vertex {n}\n".encode()
    for name in ("x", "y", "z"):
        header += f"property float {name}\n".encode()
    for name in ("nx", "ny", "nz"):
        header += f"property float {name}\n".encode()
    for i, name in enumerate(("f_dc_0", "f_dc_1", "f_dc_2")):
        header += f"property float {name}\n".encode()
    for i in range(k * 3):
        header += f"property float f_rest_{i}\n".encode()
    header += b"property float opacity\n"
    header += b"property float scale_0\nproperty float scale_1\nproperty float scale_2\n"
    header += b"property float rot_0\nproperty float rot_1\nproperty float rot_2\nproperty float rot_3\n"
    header += b"end_header\n"

    normals = np.zeros_like(xyz, dtype=np.float32)
    record = np.concatenate(
        [
            xyz.astype(np.float32),
            normals,
            sh_dc.reshape(n, 3).astype(np.float32),
            sh_rest.reshape(n, k * 3).astype(np.float32),
            opacities.reshape(n, 1).astype(np.float32),
            scales.astype(np.float32),
            rotations.astype(np.float32),
        ],
        axis=1,
    )

    with path.open("wb") as fh:
        fh.write(header)
        fh.write(record.tobytes())