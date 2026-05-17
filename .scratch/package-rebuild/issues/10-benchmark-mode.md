# `benchmark.py` orchestration + `bench.py` shim

Status: ready-for-agent

## Parent

`.scratch/package-rebuild/PRD.md`

## What to build

Create `gemma4_local/benchmark.py` with `run(prompt: str, model_ids: list[str], system: str | None, sampler: Sampler, out_path: pathlib.Path | None) -> None`. For each model id, spawn a fresh subprocess via `multiprocessing` with the `spawn` start method; in the subprocess, call `gemma4_local.model.run_once` and print one JSON line of the resulting Metrics to stdout. The parent collects the JSON lines, builds a markdown comparison table (rows = models, columns = the four Metrics fields), prints it to stdout, and additionally writes it to `out_path` if provided.

Create a `bench.py` shim at the repo root. argparse flags: `--prompt` (required), `--model` (required, repeatable — `action="append"`), `--system` / `--system-file` (mutex), `--temperature`, `--top-p`, `--max-tokens`, `--out`. Aliases resolve via `gemma4_local.model.resolve` before subprocesses are spawned.

Per `docs/adr/0001-subprocess-per-model-in-benchmark.md`, the subprocess strategy is non-negotiable: in-process model swapping would pollute `mx.metal.get_peak_memory()` across models and make the metric meaningless for comparison.

## Acceptance criteria

- [ ] `uv run bench.py --prompt "hello" --model 31b --model 26b` runs both models and prints a 2-row markdown table to stdout with TTFT, decode tokens/sec, total wall time, peak memory columns
- [ ] `--model` is repeatable; at least one is required (argparse rejects with no `--model`)
- [ ] `--out results.md` writes the same table to a file (and also prints to stdout)
- [ ] `--system` and `--system-file` work and are mutually exclusive (matching chat.py's behavior)
- [ ] Subprocesses use `multiprocessing.get_context("spawn")` (or equivalent) — not the default `fork`
- [ ] If a subprocess crashes, the parent reports the failure for that model and continues with the remaining models (the table shows successful rows; failed models are listed separately)
- [ ] Aliases resolve at the CLI boundary; subprocesses receive full HF ids
- [ ] No shared MLX state is required across subprocesses (per ADR-0001)

## Blocked by

- `09-model-run-once.md`
