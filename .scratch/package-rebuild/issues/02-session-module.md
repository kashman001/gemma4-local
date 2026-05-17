# `session` module: dataclasses, JSON persistence, tests

Status: ready-for-agent

## Parent

`.scratch/package-rebuild/PRD.md`

## What to build

Create `gemma4_local/session.py` as the persistence-and-dataclasses deep module (no MLX dependency, no model loading). It contains three frozen dataclasses — `Sampler` (`temperature`, `top_p`, `max_tokens`), `Metrics` (`ttft_ms`, `decode_tps`, `total_wall_ms`, `peak_mem_gb`), and `Session` (`model_id`, `system_prompt`, `sampler`, `messages`) — and two functions `save_session(session, path)` and `load_session(path) -> Session`.

The JSON schema includes a schema-version field so future evolution is possible without silent breakage. Loading a file with a missing or unknown version raises a clear, typed error.

Add `pytest` to `pyproject.toml` as a dev dependency, create `tests/` at the repo root, and write `tests/test_session.py` covering: roundtrip with all fields populated, roundtrip with `system_prompt=None`, unknown/missing schema-version raises.

## Acceptance criteria

- [ ] `gemma4_local/session.py` defines `Sampler`, `Metrics`, `Session` as frozen dataclasses (use `@dataclass(frozen=True)`)
- [ ] `save_session(session, path)` writes JSON containing `schema_version`, `model_id`, `system_prompt`, `sampler` (nested), `messages`
- [ ] `load_session(path)` returns a `Session` equal to the saved one
- [ ] Loading a JSON file with an unknown or missing `schema_version` raises a typed error with a clear message (not a `KeyError` or `JSONDecodeError`)
- [ ] No imports from `mlx`, `mlx_lm`, or any model-loading code in this module
- [ ] `pytest` is in `pyproject.toml` under a dev-deps group (or `[project.optional-dependencies]`)
- [ ] `tests/test_session.py` covers the three cases above and passes via `uv run pytest`
- [ ] All tests run in <500 ms total

## Blocked by

- `01-bootstrap-package.md`
