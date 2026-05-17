# README updates: benchmark section, aliases, slash commands

Status: ready-for-agent

## Parent

`.scratch/package-rebuild/PRD.md`

## What to build

Update `README.md` to reflect the rebuilt project. Three additions, no removals (existing `uv run chat.py` invocation must continue to be documented unchanged):

1. A **Benchmark** section under Usage showing `uv run bench.py --prompt "..." --model 31b --model 26b` and a sample output table.
2. A short **Model aliases** subsection documenting the three aliases (`31b`, `26b`, `e4b`) and stating that any non-alias string is treated as a literal Hugging Face id.
3. A **Slash commands** subsection under the chat-mode usage section, listing all seven commands (`/help`, `/reset`, `/system`, `/save`, `/load`, `/model`, `/tokens`) with a one-line description each, plus `exit`.

Also add a one-line mention of the new CLI flags on chat.py: `--model --system / --system-file --temperature --top-p --max-tokens --sessions-dir`.

## Acceptance criteria

- [ ] Existing Quickstart / one-shot generation / interactive chat / server sections are intact
- [ ] New "Benchmark" subsection appears under Usage with a working `uv run bench.py` example
- [ ] "Model aliases" subsection lists exactly the three aliases shipping in `gemma4_local/model.py`
- [ ] "Slash commands" subsection lists all 7 commands plus `exit`, each with a one-line description
- [ ] Chat-mode CLI flags are mentioned (one line is enough; full reference lives in `--help`)
- [ ] No claims that contradict the actual implemented behavior (verify each example by running it)

## Blocked by

- `10-benchmark-mode.md`
