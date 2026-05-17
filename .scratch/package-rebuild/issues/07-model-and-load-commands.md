# `/model` swap + `/load` with model-mismatch prompt

Status: ready-for-agent

## Parent

`.scratch/package-rebuild/PRD.md`

## What to build

Add `/model <alias-or-id>` to the REPL. It resolves the argument via `gemma4_local.model.resolve()`, unloads the current model, and loads the new one in-process. The user is told the load is happening (~30s). After the swap, messages and system prompt are preserved; the user continues the conversation against the new model.

Add `/load <path>` to the REPL. It reads the file via `gemma4_local.session.load_session`. If the saved Session's `model_id` differs from the currently loaded model, prompt `[y/N]` to swap before continuing — yes triggers a `/model`-equivalent swap, no aborts the load entirely. The saved sampler is applied silently (no prompt). The saved system prompt and messages are restored unconditionally.

## Acceptance criteria

- [ ] `/model 26b` reloads the model in-process and the next response comes from the new model (manual verify)
- [ ] `/model some-other-org/some-model` works the same way (passthrough)
- [ ] After `/model`, the existing message history and system prompt are intact
- [ ] `/load path.json` reads the file and, if `model_id` matches the current model, restores state silently
- [ ] `/load path.json` with a different `model_id` prompts the user `[y/N]`; `y` swaps the model, `n` aborts the entire load
- [ ] When `/load` succeeds, the sampler, system prompt, and messages from the file are all in effect
- [ ] Errors from `load_session` (missing file, malformed JSON, unknown schema version) are shown to the user; the REPL does not crash
- [ ] Round-trip works: `/save foo.json`, exit, restart, `/load foo.json` restores everything

## Blocked by

- `06-save-command.md`
