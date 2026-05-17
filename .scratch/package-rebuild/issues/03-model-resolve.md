# `model.resolve()` with alias table + tests

Status: ready-for-agent

## Parent

`.scratch/package-rebuild/PRD.md`

## What to build

Create `gemma4_local/model.py` with an `ALIASES` dict and a `resolve(model_id_or_alias: str) -> str` function. Three aliases ship: `31b` → `mlx-community/gemma-4-31B-it-OptiQ-4bit`, `26b` → `mlx-community/gemma-4-26b-a4b-it-4bit`, `e4b` → `mlx-community/gemma-4-e4b-it-OptiQ-4bit`. Anything not in the alias table passes through as a literal Hugging Face id — `resolve` is the only place that knows about aliases, and it never validates whether the result is a real model.

Write `tests/test_aliases.py` covering all three branches: known alias resolves to the expected HF id, an arbitrary `org/name` string passes through unchanged, an unknown short string passes through unchanged.

`model.py` should expose only `ALIASES` and `resolve()` in this slice. `load()` and `run_once()` come later.

## Acceptance criteria

- [ ] `gemma4_local/model.py` defines `ALIASES: dict[str, str]` with exactly three entries (`31b`, `26b`, `e4b`)
- [ ] `resolve()` returns the HF id for known aliases
- [ ] `resolve()` returns its input unchanged for any string not in `ALIASES` (including unknown short names and full HF ids)
- [ ] `resolve()` does not call out to the network or load a model
- [ ] `tests/test_aliases.py` covers all three branches and passes via `uv run pytest`
- [ ] No MLX import in `model.py` is required by this slice (it can be added when `load()` lands later)

## Blocked by

- `01-bootstrap-package.md`
