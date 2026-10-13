# Security Policy

## Scope

`gaussian-splat-photo-forge` is a local desktop tool. It reads image folders,
writes `.ply` / `.splat` files, and optionally launches COLMAP as a subprocess.
It does not phone home, does not upload your photos, and does not run any
remote code.

## Threat model

- **Malicious input images**: We use Pillow for image loading. Pillow has a
  history of crafted-image CVEs. We pin a patched version in
  `requirements.txt` and recommend users run the tool on trusted photo sets.
- **Subprocess invocation**: COLMAP is launched via `subprocess.run` with a
  list of args (never `shell=True`). Paths are validated.
- **PLY parsing**: Our `.ply` reader is strict and bounded. Malformed headers
  raise `SplatIOError` instead of crashing the process.

## Reporting a vulnerability

Email `security@gsforge.example` or open a private security advisory on the
GitHub repo. Please include a minimal reproducer. We aim to respond within
72 hours.

## Supported versions

Only the latest tagged release receives security fixes.