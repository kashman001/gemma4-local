# System prompt: flags + `/system` slash commands

Status: ready-for-agent

## Parent

`.scratch/package-rebuild/PRD.md`

## What to build

Add `--system "text"` and `--system-file path` to the root `chat.py` argparse parser. The two flags are mutually exclusive (use argparse's `add_mutually_exclusive_group`). Either source produces a single `system_prompt: str | None` that is passed into `gemma4_local.chat.run()`.

When a system prompt is set, the REPL inserts `{"role": "system", "content": system_prompt}` at index 0 of `messages` before each call to `tokenizer.apply_chat_template`. Verified during the grilling-session spike: the Gemma 4 chat template accepts `role: system` directly — no fallback "prepend into first user turn" code path is needed.

Add two slash commands in the chat REPL: `/system <text>` replaces the current system prompt; `/system` (no argument) clears it (sets to `None`). The change takes effect on the next turn.

## Acceptance criteria

- [ ] `--system` and `--system-file` flags exist and are mutually exclusive (argparse rejects using both)
- [ ] `--system-file path` reads the file's contents as UTF-8 and uses them as the system prompt
- [ ] `gemma4_local.chat.run()` accepts `system_prompt: str | None`
- [ ] When `system_prompt` is non-None, `{"role": "system", "content": system_prompt}` is at index 0 of messages on every generation call
- [ ] `/system <text>` replaces the system prompt and the next response reflects the new persona
- [ ] `/system` (no argument) clears it; next response no longer reflects the old persona
- [ ] System prompt persists across `/reset` is NOT required — `/reset` clears messages only; system prompt handling on reset can match whatever feels natural (document the choice in the PR description)

## Blocked by

- `04-chat-cli-flags.md`
