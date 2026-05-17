# `/save` slash command

Status: ready-for-agent

## Parent

`.scratch/package-rebuild/PRD.md`

## What to build

Add `/save [path]` to the REPL's slash-command dispatch. With no argument, writes the current Session to `<sessions_dir>/<ISO-timestamp>.json` (default sessions_dir is `./sessions`, overridable via `--sessions-dir`). With an argument, writes to exactly the path given. The sessions directory is lazily created if missing.

The serialized Session contains the current model id (resolved), system prompt (or null), sampler (the three numeric fields), and the full messages list — using `gemma4_local.session.save_session`.

## Acceptance criteria

- [ ] `/save` (no argument) writes to `<sessions_dir>/<ISO-8601-timestamp>.json` and prints the saved path to the user
- [ ] `/save my-session.json` writes to exactly `my-session.json`
- [ ] The sessions directory is created with `mkdir(parents=True, exist_ok=True)` if missing
- [ ] The written JSON validates against `gemma4_local.session.load_session` (roundtrip works)
- [ ] The saved `model_id` is the resolved HF id, not the user-typed alias
- [ ] If `save_session` raises, the error message is shown to the user; the REPL does not crash

## Blocked by

- `02-session-module.md`
- `05-system-prompt.md`
