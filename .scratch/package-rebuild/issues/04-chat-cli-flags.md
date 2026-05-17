# chat.py CLI flags + alias resolution at startup

Status: ready-for-agent

## Parent

`.scratch/package-rebuild/PRD.md`

## What to build

Add argparse to the root `chat.py` shim with five flags: `--model`, `--temperature`, `--top-p`, `--max-tokens`, `--sessions-dir`. Defaults come from `gemma4_local.defaults.DEFAULTS`. The parsed `--model` value is run through `gemma4_local.model.resolve()` exactly once at startup; everything downstream sees a resolved HF id.

`gemma4_local.chat.run()` is updated to accept these as parameters (model_id, sampler, sessions_dir) rather than reading them from module-level constants. Aliases work end-to-end: `uv run chat.py --model 31b` is equivalent to passing the full HF id; an unknown short string or a full HF id pass through unchanged and are handed to `mlx_lm.load`.

## Acceptance criteria

- [ ] Root `chat.py` exposes five argparse flags with defaults from `DEFAULTS`
- [ ] Help output (`uv run chat.py --help`) lists each flag with its default value
- [ ] `--model 31b` resolves to `mlx-community/gemma-4-31B-it-OptiQ-4bit` before the model is loaded
- [ ] `--model some-other-org/some-model` is passed through unchanged
- [ ] `gemma4_local.chat.run()` signature takes `model_id: str`, `sampler: Sampler`, `sessions_dir: pathlib.Path` (no module-level state read)
- [ ] `--temperature`, `--top-p`, `--max-tokens` change generation behavior at runtime (manual verify in REPL)
- [ ] Existing `uv run chat.py` (no flags) still works and uses defaults

## Blocked by

- `01-bootstrap-package.md`
- `03-model-resolve.md`
