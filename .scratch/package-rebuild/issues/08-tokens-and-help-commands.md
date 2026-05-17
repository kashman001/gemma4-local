# `/tokens` and `/help` slash commands

Status: ready-for-agent

## Parent

`.scratch/package-rebuild/PRD.md`

## What to build

Add `/help` to the REPL: prints a one-line description of every slash command (`/help`, `/reset`, `/system`, `/save`, `/load`, `/model`, `/tokens`) plus `exit`.

Add `/tokens` to the REPL: prints time-to-first-token, total output tokens, decode tokens/sec, and total wall time for the most recent assistant response. If no response has been generated yet in this session, print a friendly "no responses yet" message.

This requires the REPL to time each streamed generation: capture `t0 = perf_counter()` before the `stream_generate` call, capture `t_first` on receipt of the first chunk, count chunks as decoded tokens (or use tokenizer length on the assembled text), capture `t_end` after the loop. Store the latest measurement on a small holder so `/tokens` can read it.

These are the simplest two commands in the set and intentionally bundled.

## Acceptance criteria

- [ ] `/help` lists all 7 slash commands plus `exit`, each with a one-line description
- [ ] `/tokens` after at least one response prints TTFT (ms), token count, decode tokens/sec, and wall time
- [ ] `/tokens` with no prior response prints a friendly message and does not error
- [ ] Timing instrumentation does not visibly slow the streamed output
- [ ] `/help`, `/tokens`, and the previously-existing `/reset` are all still routed correctly by the slash-command dispatcher

## Blocked by

- `04-chat-cli-flags.md`
