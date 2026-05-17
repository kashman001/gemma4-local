# CLAUDE.md

## Project

Single-script sandbox for running Gemma 4 on Apple Silicon via MLX. Entry point: `chat.py`. Model swapped via the `MODEL` constant.

## Environment

- `uv` manages the venv and lockfile. Always run via `uv run …` — don't activate `.venv` manually or call `python` directly.
- Python is pinned to 3.12 (MLX wheels for 3.14 are unreliable). Don't bump it.
- MLX/mlx-lm only work on Apple Silicon. Don't add cross-platform shims.
- First model pull is ~18 GB into `~/.cache/huggingface/hub/`. Don't redownload casually.

## Working style

**Think before coding.** State assumptions. If multiple interpretations exist, surface them. If something's unclear, ask — don't guess.

**Simplicity first.** Minimum code that solves the problem. No speculative abstractions, no error handling for impossible cases, no "flexibility" that wasn't requested. This is a sandbox — keep it that way.

**Surgical changes.** Touch only what the task requires. Match existing style. Don't refactor adjacent code or delete pre-existing dead code unsolicited.

**Goal-driven.** For multi-step tasks, state a brief plan with a verify check per step before executing.

## Agent skills

### Issue tracker

Local markdown under `.scratch/<feature>/` — no remote tracker. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical defaults (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), written on a `Status:` line in each issue file. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context. `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
