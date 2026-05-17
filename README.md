# gemma4-local

A minimal sandbox for running **Google Gemma 4 31B** fully on-device on Apple Silicon via Apple's **MLX** framework. No cloud APIs, no telemetry — weights and inference live entirely in unified memory.

## Model

[`mlx-community/gemma-4-31B-it-OptiQ-4bit`](https://huggingface.co/mlx-community/gemma-4-31B-it-OptiQ-4bit) — a mixed-precision 4-bit OptiQ quant of `google/gemma-4-31B-it`. OptiQ keeps sensitivity-critical layers at 8-bit and the rest at 4-bit, staying near uniform-4-bit size (~18 GB) with better quality.

Cached under `~/.cache/huggingface/hub/` on first use.

## Requirements

- Apple Silicon Mac (M1 or newer). Tested target: M5 Max, 128 GB unified memory.
- ~36 GB unified memory recommended for the 31B model with comfortable headroom.
- Python 3.12 (pinned via `uv` — MLX wheels for 3.14 are not yet reliable).

## Setup

```sh
uv sync
```

This installs `mlx`, `mlx-lm`, and their dependencies into a local `.venv`.

## Usage

**One-shot generation:**

```sh
uv run mlx_lm.generate \
  --model mlx-community/gemma-4-31B-it-OptiQ-4bit \
  --prompt "Explain unified memory on Apple Silicon." \
  --max-tokens 400
```

**Interactive chat REPL** (streaming, multi-turn history, slash commands, persistable sessions):

```sh
uv run chat.py
```

Flags: `--model`, `--temperature`, `--top-p`, `--max-tokens`, `--system "text"` / `--system-file path`, `--sessions-dir DIR`. Run `uv run chat.py --help` for the full list with defaults.

Slash commands (type `/help` inside the REPL for the same list):

| Command | What it does |
|---|---|
| `/help` | Show the command list |
| `/reset` | Clear conversation history |
| `/system <text>` | Set the system prompt; `/system` alone clears it |
| `/save [path]` | Save the current session to `<sessions_dir>/<timestamp>.json` (or to `<path>`) |
| `/load <path>` | Load a saved session; prompts before swapping the model if it differs |
| `/model <alias-or-id>` | Swap to a different model in-process (~30s reload) |
| `/tokens` | Show TTFT / token count / decode tokens-per-second / wall time for the last response |
| `exit` | Quit (Ctrl-D / Ctrl-C also work) |

**Benchmark** mode runs the same prompt across one or more models in fresh subprocesses (so peak-memory readings stay clean — see [ADR-0001](docs/adr/0001-subprocess-per-model-in-benchmark.md)) and prints a markdown comparison table:

```sh
uv run bench.py --prompt "explain unified memory on Apple Silicon" --model 31b --model 26b
```

Flags: `--prompt` (required), `--model` (repeatable, required), `--system` / `--system-file`, `--temperature`, `--top-p`, `--max-tokens`, `--out path.md` (writes the table to a file in addition to stdout). Run `uv run bench.py --help` for defaults.

Output columns: TTFT (ms), decode tokens/sec, total wall time (ms), peak unified memory (GB). A sample run on an M5 Max with the prompt `"explain unified memory on Apple Silicon in one short paragraph"` (200-token cap):

| model | TTFT (ms) | decode (tok/s) | total (ms) | peak mem (GB) |
|---|---|---|---|---|
| `mlx-community/gemma-4-31B-it-OptiQ-4bit` | 493.5 | 21.8 | 9665.0 | 21.10 |
| `mlx-community/gemma-4-26b-a4b-it-4bit` | 388.0 | 123.2 | 2011.0 | 13.55 |

The 26B MoE decodes ~5.6× faster than the 31B dense and uses ~7.6 GB less unified memory at peak.

**OpenAI-compatible HTTP server** for use with Cline, Continue, or any OpenAI SDK client:

```sh
uv run mlx_lm.server \
  --model mlx-community/gemma-4-31B-it-OptiQ-4bit \
  --host 127.0.0.1 --port 8080
```

Point clients at `http://127.0.0.1:8080/v1` with any non-empty API key.

## Swapping the model

Pass `--model` to `chat.py` or `bench.py`, or use `/model <alias-or-id>` inside the chat REPL. Two short aliases ship out of the box:

| Alias | Model id | Notes |
|---|---|---|
| `31b` | `mlx-community/gemma-4-31B-it-OptiQ-4bit` | default; 31B dense |
| `26b` | `mlx-community/gemma-4-26b-a4b-it-4bit` | 26B MoE with 4B active params — measured at ~5.6× faster decode than 31B dense at ~36% less peak memory (see the Benchmark section), near-equivalent quality |

Anything that isn't an alias is passed through as a literal Hugging Face id, so `--model some-org/some-model` works too. The default (when `--model` is omitted) lives in `gemma4_local/defaults.py`.

> **Note on `e4b`:** the `mlx-community/gemma-4-e4b-it-OptiQ-4bit` checkpoint uses a newer attention variant (KV-norm) that the pinned `mlx-lm>=0.31.3` doesn't yet load — it errors out with `ValueError: Received N parameters not in model`. Once upstream `mlx-lm` catches up, the alias will return.

## Troubleshooting

- **First run is slow / appears to hang:** it's downloading ~18 GB. Pre-pull with `uv run python -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/gemma-4-31B-it-OptiQ-4bit')"`.
- **Out of memory:** close memory-heavy apps, or switch to the 26B MoE variant (`--model 26b`).
- **Generation stops early:** raise `--max-tokens` (CLI) or the `max_tokens` value in `gemma4_local/defaults.py`.
