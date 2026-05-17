# Package rebuild

Status: ready-for-agent

## Problem Statement

The current `gemma4-local` sandbox is a single 55-line `chat.py` that loads one hard-coded model and talks to it. Five concrete friction points block its stated purpose (evaluating Gemma 4 variants on Apple Silicon):

1. Sampling parameters and the model id are hard-coded constants — experimenting requires a code edit and a restart.
2. There is no way to give the model a system prompt / persona.
3. The REPL has only two commands (`/reset`, `exit`). A multi-hour session can't be saved or resumed; the model can't be swapped mid-session; there is no way to inspect token usage.
4. There is no way to compare two models on the same prompt. The README documents three swap candidates (31B dense, 26B MoE, e4b) but offers no way to decide between them empirically.
5. Everything lives in one file. A benchmark feature that needs to run models in fresh subprocesses (per ADR-0001) cannot share code cleanly with the REPL.

## Solution

Rebuild `gemma4-local` as a small Python package with two thin entry-point scripts at the repo root:

- `chat.py` — interactive REPL with a richer slash-command surface, persistable Sessions, runtime-configurable sampling, system-prompt support, and the ability to swap models without restarting the process.
- `bench.py` — a benchmark runner that takes one prompt and one or more model ids/aliases, runs each model in a fresh subprocess to get clean per-model peak-memory readings, and prints a comparison table.

Users still install with `uv sync` and run `uv run chat.py` exactly as the README describes today. The "minimal sandbox" character of the project is preserved: still Apple-Silicon-only, still no telemetry, still no daemon. The user-visible change is "more knobs and a benchmark," not "a different kind of tool."

## User Stories

1. As a researcher, I want to set the model, sampling temperature, top-p, and max-tokens via CLI flags, so that I can try a configuration without editing source.
2. As a researcher, I want to specify a system prompt inline (`--system "you are X"`), so that I can quickly test how a persona shifts a single-prompt experiment.
3. As a researcher, I want to specify a system prompt from a file (`--system-file path`), so that multi-paragraph instructions don't need to be quoted on a shell command line.
4. As a researcher, I want `--system` and `--system-file` to be mutually exclusive, so that the source of the system prompt is unambiguous.
5. As a researcher, I want to change the system prompt mid-session via `/system <text>`, so that I can iterate on personas without paying a 30-second model reload.
6. As a researcher, I want `/system` with no argument to clear the system prompt, so that I can return to a baseline without restarting.
7. As a researcher, I want to refer to the Gemma 4 variants by short aliases (`31b`, `26b`, `e4b`), so that I don't have to type or remember the full `mlx-community/...` ids.
8. As a researcher, I want any model id not in the alias table to pass through as a literal Hugging Face id, so that I can still point at a custom or new model without touching the alias table.
9. As a researcher, I want `/help` to list all slash commands, so that I can discover features without re-reading the README.
10. As a researcher, I want `/reset` to clear the message history, so that I can start a fresh conversation in the current process.
11. As a researcher, I want `/save` (no argument) to persist the current Session to `./sessions/<ISO-timestamp>.json`, so that quick saves don't require me to invent a name.
12. As a researcher, I want `/save <path>` to honor the path I specified, so that I can save to a meaningful filename when I'm preserving something I'll come back to.
13. As a researcher, I want `/load <path>` to restore a previously saved Session (messages, system prompt, sampler), so that I can resume work across REPL restarts.
14. As a researcher, I want `/load` to prompt before swapping the model if the saved Session was for a different model than the one currently loaded, so that I don't lose 30 seconds and 18 GB of memory unintentionally.
15. As a researcher, I want `/load` to silently apply the sampler from the saved Session, so that the saved state is faithfully restored without a noisy confirmation for a cheap change.
16. As a researcher, I want `/model <alias-or-id>` to swap the loaded model in the current REPL, so that I can compare model responses on a shared message history.
17. As a researcher, I want `/tokens` to show how many tokens the last response consumed and how long it took, so that I have visibility into cost-of-generation without instrumenting code.
18. As a researcher, I want `exit` (or Ctrl-D / Ctrl-C) to quit cleanly, so that I don't need to kill the process.
19. As a researcher, I want my saved Sessions to record the model id, system prompt, sampler, and full message history, so that loading reconstructs exactly the state I had.
20. As a researcher, I want the JSON Session schema to be human-inspectable with `jq`, so that I can debug or hand-edit a saved file if I need to.
21. As a researcher, I want to run `uv run bench.py --prompt "X" --model 31b --model 26b`, so that I can compare two specific models on a single prompt I care about.
22. As a researcher, I want the benchmark to report time-to-first-token, decode tokens/sec, total wall time, and peak unified memory for each model, so that I have the four numbers that actually decide a model-swap choice.
23. As a researcher, I want each benchmarked model to run in a fresh subprocess, so that the peak-memory number for model B is not polluted by model A's allocations (see ADR-0001).
24. As a researcher, I want the benchmark output as a markdown table on stdout by default, so that I can copy-paste it directly into notes or a PR description.
25. As a researcher, I want `--out path.md` to additionally write the table to a file, so that I can archive a benchmark run alongside its prompt.
26. As a researcher, I want benchmark mode to accept the same `--system` / `--system-file` flags as chat mode, so that I can benchmark behavior under a persona.
27. As a researcher, I want benchmark to share the same alias table as chat, so that `31b` means the same thing everywhere.
28. As a researcher, I want the package importable as `gemma4_local`, so that I can drive the chat loop or a single benchmark run from a notebook or ad-hoc script.
29. As a researcher, I want the README's existing `uv run chat.py` examples to continue working unchanged, so that nothing I've already learned about the project is invalidated.
30. As a maintainer, I want defaults to live as code constants in one place, so that changing the default temperature is a one-line edit, not a config-file dance.
31. As a maintainer, I want `gemma4_local.model.run_once` to be subprocess-safe (no module-level state), so that the benchmark's process-per-model strategy works correctly.
32. As a maintainer, I want alias resolution and Session JSON roundtrip to be covered by fast, model-free unit tests, so that the high-value pure-logic surface is regression-protected without paying for a model load on every test run.

## Implementation Decisions

**Project shape.**
- The repo becomes a small Python package `gemma4_local` with two thin root-level entry-point scripts. `chat.py` and `bench.py` at the root each contain a few lines of argparse parsing and call into the package. No unified subcommand CLI (no `gemma4 chat` / `gemma4 bench`) — two entry points keeps each parser focused and preserves the README's existing invocation.
- The package is split into five modules: `defaults` (pure data — `DEFAULTS` and `ALIASES` tables), `session` (the persistence-and-dataclasses deep module — see below), `model` (alias resolution, MLX load, the subprocess-safe `run_once`), `chat` (the REPL loop and slash-command dispatch), `benchmark` (subprocess orchestration and table formatting).
- argparse from the standard library only. No `click` / `typer` dependency. The CLI surface is small enough that argparse is the right size.

**`session` as a deep module.**
- `session` owns the three small frozen dataclasses (`Sampler`, `Metrics`, `Session`) and the two persistence functions (`save_session`, `load_session`). It has no MLX dependency and no model-loading dependency.
- Putting `Sampler` and `Metrics` in `session` rather than `model` produces a deeper boundary: `session`'s interface is "five names, all pure data and pure functions," it encapsulates the on-disk JSON schema, and it can be tested in isolation in milliseconds.
- The JSON schema is `{"model_id": str, "system_prompt": str | null, "sampler": {temperature, top_p, max_tokens}, "messages": [{role, content}, ...]}`. A schema-version field is included to allow future evolution; missing/unknown versions raise a clear error rather than silently misloading.

**`model.run_once` contract (constrained by ADR-0001).**
- `gemma4_local.model.run_once(model_id, prompt, system, sampler) -> Metrics` is the benchmark's subprocess entry point. It must be subprocess-safe: no module-level mutable state, no caching of loaded models or tokenizers across calls. It is allowed to assume it owns the process.
- Benchmark spawns one subprocess per model via `multiprocessing` with the `spawn` start method, collects a Metrics payload from each, and aggregates.

**System prompt mechanics.**
- The Gemma 4 chat template accepts `{"role": "system", "content": ...}` as `messages[0]` directly — verified against the pinned `mlx-lm` version by a spike during the grilling session. The implementation just inserts a system entry at index 0; no fallback "prepend to first user turn" code path is needed.
- Spike output (compressed): `apply_chat_template([{role: system, content: "X"}, {role: user, content: "hi"}], add_generation_prompt=True)` produces a template with an explicit `system` turn. The baseline (no system message) still emits an empty system slot, which is a template quirk but does not affect the API.

**Defaults and aliases.**
- Defaults live in `gemma4_local.defaults.DEFAULTS` as a plain dict. CLI flags override defaults. No config file, no environment variable layer.
- Three aliases ship: `31b` → `mlx-community/gemma-4-31B-it-OptiQ-4bit`, `26b` → `mlx-community/gemma-4-26b-a4b-it-4bit`, `e4b` → `mlx-community/gemma-4-e4b-it-OptiQ-4bit`. Anything else is passed through as a literal Hugging Face model id. Alias resolution happens at the CLI/REPL boundary exactly once; internal code paths always pass resolved model ids.

**Persistence.**
- Default save destination if `/save` is given no argument: `./sessions/<ISO-timestamp>.json`. The directory is lazily created. A `--sessions-dir` CLI flag overrides the default directory.
- `/load` reads the JSON, prompts the user (`[y/N]`) before swapping the model if `model_id` differs from the currently loaded model, and silently applies the saved sampler. System prompt and messages are restored unconditionally.

**Benchmark metrics.**
- The four metrics — TTFT (ms), decode tokens/sec, total wall (ms), peak memory (GB) — are gathered using `mlx.metal.get_peak_memory()` and `mlx.metal.reset_peak_memory()`, both of which exist in the pinned `mlx>=0.31.2` (verified via spike). Wall-clock and TTFT timing use `time.perf_counter()` around the `stream_generate` call.
- Output is a stdout markdown table by default. `--out path.md` additionally writes the table to a file. No `rich` dependency; no CSV/JSON output format.

**Out-of-package shim files.**
- The root-level `chat.py` and `bench.py` are 5–10 line argparse-and-dispatch shims. All real logic lives in the package modules. This keeps the README's `uv run chat.py` invocation working with no semantic change.

## Testing Decisions

A good test in this codebase exercises external behavior of a pure-logic surface and runs in milliseconds without loading a model. The model-loading paths are explicitly *not* tested — they require ~18 GB of weights, are I/O-bound on first run, and offer almost no logic worth catching with assertions; manual smoke-testing in the REPL covers them better. Tests are added to a new `tests/` directory; `pytest` is added to `pyproject.toml` as a dev dependency.

**Modules tested:**

- `gemma4_local.model.resolve` (alias resolution).
  - `resolve("31b")` returns the expected `mlx-community/...` id.
  - `resolve("mlx-community/some-other-model")` passes through unchanged.
  - `resolve("not-a-known-alias")` passes through unchanged (the model loader's job to fail later, not `resolve`'s).
- `gemma4_local.session.save_session` and `load_session` (JSON roundtrip).
  - Roundtrip a Session with all fields populated; `load_session(save_session(s)) == s`.
  - Roundtrip a Session with `system_prompt=None` cleanly.
  - Loading a JSON document with an unknown/missing schema-version field raises a clear, typed error rather than silently producing a malformed Session.

**Prior art:** there is no prior test setup in this repo. The tests will establish the convention: one test file per module under test, pytest discovery from the repo root, no shared fixtures heavier than dataclass construction.

Modules with model-loading or REPL-loop behavior — `model.load`, `model.run_once`, `chat`, `benchmark` — are left to manual verification by running `uv run chat.py` and `uv run bench.py`.

## Out of Scope

The grilling session deliberately rejected the following, all of which can be revisited later as separate PRDs:

- Live sampler-tuning slash commands (`/temp`, `/top-p`, `/max`). Sampling iteration is what `bench.py` is for; adding the same knobs in chat creates two places to think about the same state.
- A built-in benchmark prompt suite. Choosing "representative" prompts is a research project, not a sandbox feature. Users pass a `--prompt` they care about.
- Sampling-sweep mode (benchmark varying temperature/top-p over a fixed model+prompt).
- Replay-from-saved-Session in benchmark mode. Cute but couples chat and bench, and is only meaningful with `temperature=0`.
- Configuration file (TOML/YAML) or environment-variable layer for defaults. The repo has one user; flag-overrides-constant is sufficient.
- Markdown or human-readable export format for Sessions. The JSON file is the canonical form; `jq .` is the inspection tool.
- Auto-save of every turn. Explicit `/save` only.
- Cross-platform support. MLX is Apple Silicon only and the README is explicit about this.
- A unified subcommand CLI (`gemma4 chat`, `gemma4 bench`). Two entry-point scripts is the right size for two modes; revisit if a third mode is ever added.
- `rich` / `textual` or any other terminal-UI dependency. Plain `print` and a markdown table is enough.
- Integration tests that exercise model loading.

## Further Notes

- ADR-0001 (`docs/adr/0001-subprocess-per-model-in-benchmark.md`) is the authoritative record of the subprocess-per-model decision and the resulting subprocess-safety constraint on `model.run_once`. Read it before touching `benchmark.py`.
- `CONTEXT.md` at the repo root defines the precise meanings of *Session*, *Sampler*, *Metrics*, *model id*, and *alias*. Use those terms verbatim in code, comments, and tests; avoid drifting to synonyms.
- `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, and `docs/agents/domain.md` describe the repo's local-markdown issue convention and the canonical triage labels.
- Two spikes were run during the grilling session and are summarized inline above: (i) the Gemma 4 chat template accepts `role: system` directly, eliminating a planned fallback code path; (ii) `mlx.metal.get_peak_memory` and `reset_peak_memory` both exist in the pinned MLX version, making the peak-memory metric reachable.
- The README must be lightly updated when this work lands: add a short "Benchmark" section pointing at `uv run bench.py`, document the three model aliases, and document the slash-command list. The existing chat-mode invocation does not change.
