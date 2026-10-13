# Contributing to gaussian-splat-photo-forge

Thanks for wanting to help turn photos into 3D Gaussian splats. This repo is a
Python toolkit that ingests a folder of overlapping photos, runs the standard
SfM + 3DGS pipeline, and exports `.ply` / `.splat` scenes viewable in any
WebGL splat viewer.

## Dev environment

```bash
git clone https://github.com/<you>/gaussian-splat-photo-forge
cd gaussian-splat-photo-forge
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
pip install -e .
```

## Pipeline stages you can plug into

The core pipeline is a chain of `Stage` objects under
`src/gsforge/pipeline/`. Each stage declares `name`, `requires`, and
`produces`. If you're adding a new SfM backend (e.g. GLOMAP instead of
COLMAP), drop it in `src/gsforge/reconstruct/` and register it in
`src/gsforge/pipeline/registry.py`.

## Style

- Ruff for lint + format: `ruff check . && ruff format .`
- Type hints everywhere. `mypy --strict src/gsforge` should pass.
- No global mutable state in stages — pass a `PipelineContext`.
- Log with `logging.getLogger(__name__)`, never `print`.

## Tests

```bash
pytest -q
pytest tests/test_splat_io.py -k ply -vv
```

GPU tests are marked `@pytest.mark.cuda` and skipped on CPU-only boxes.

## PR checklist

- [ ] Ran `ruff` and `mypy`
- [ ] Added a test for the new stage or IO format
- [ ] Updated `docs/` if you changed a CLI flag
- [ ] Tested on at least one real photo set (10–200 images)

## Reporting bugs

Open a GitHub issue with: OS, GPU, driver version, `pip freeze` output, and
the command you ran. Attach the failing log if possible.