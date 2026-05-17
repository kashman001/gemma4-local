# Bootstrap package; centralize defaults

Status: ready-for-agent

## Parent

`.scratch/package-rebuild/PRD.md`

## What to build

Create the `gemma4_local` Python package and move the current 55-line REPL out of the root `chat.py` into `gemma4_local/chat.py` (a new `run()` function). Create `gemma4_local/defaults.py` containing a `DEFAULTS` dict for `model_id`, `temperature`, `top_p`, `max_tokens`, and `sessions_dir`. The new `chat.py` and `defaults.py` together must reproduce today's behavior exactly — same default model, same constants, same `/reset` and `exit` commands.

The root `chat.py` becomes a tiny shim: import and call `gemma4_local.chat.run`. No CLI flags yet. The existing `uv run chat.py` invocation must work unchanged and produce identical user-visible behavior.

## Acceptance criteria

- [ ] `gemma4_local/__init__.py`, `gemma4_local/chat.py`, `gemma4_local/defaults.py` exist
- [ ] `gemma4_local/defaults.py` exports `DEFAULTS` dict with the five keys above; values match the current hardcoded constants
- [ ] `gemma4_local/chat.py` exposes a `run()` function containing the REPL loop, with constants sourced from `DEFAULTS`
- [ ] Root `chat.py` is ≤10 lines and only imports + calls `gemma4_local.chat.run`
- [ ] `uv run chat.py` launches the REPL with identical behavior to before this change
- [ ] `python -c "import gemma4_local.chat"` succeeds (package is importable)

## Blocked by

None — can start immediately.
