# `model.run_once`: subprocess-safe single-model runner

Status: ready-for-agent

## Parent

`.scratch/package-rebuild/PRD.md`

## What to build

Add `run_once(model_id: str, prompt: str, system: str | None, sampler: Sampler) -> Metrics` to `gemma4_local/model.py`. This is the function the benchmark will invoke inside a fresh subprocess per model. It loads the model + tokenizer, applies the chat template (with the system prompt as `messages[0]` if non-None), runs generation, measures the four metrics, and returns a `Metrics` object.

**Subprocess-safety constraint (per `docs/adr/0001-subprocess-per-model-in-benchmark.md`):** no module-level mutable state in `model.py`, no caching of loaded models or tokenizers across calls. The function assumes it owns the process and does not need to clean up.

Measurement details:
- Call `mx.metal.reset_peak_memory()` immediately before generation begins.
- TTFT: `perf_counter()` delta from the start of `stream_generate` to receipt of the first chunk.
- Decode tokens/sec: total output tokens divided by (total wall time minus TTFT). Use chunk count or tokenizer encoding of the assembled output.
- Total wall: `perf_counter()` delta across the full generation call.
- Peak memory: `mx.metal.get_peak_memory()` after generation, converted to GB.

Verified during the grilling-session spike: `get_peak_memory` and `reset_peak_memory` both exist in the pinned `mlx>=0.31.2`.

## Acceptance criteria

- [ ] `run_once` signature is exactly `(model_id: str, prompt: str, system: str | None, sampler: Sampler) -> Metrics`
- [ ] No module-level mutable state in `gemma4_local/model.py` (only constants and pure functions at module scope)
- [ ] Calling `run_once` twice in the same process returns reasonable Metrics both times (the constraint is about the *benchmark* using subprocesses; the function itself must still be callable, just not optimal)
- [ ] System prompt, when non-None, appears as `messages[0]` with `role="system"`
- [ ] All four Metrics fields are populated with reasonable values (manual verify via a one-line script)
- [ ] Peak memory is measured using `mx.metal.reset_peak_memory()` + `mx.metal.get_peak_memory()` per the spike
- [ ] No regression in `tests/test_aliases.py`

## Blocked by

- `02-session-module.md`
- `03-model-resolve.md`
