"""Entrypoint for `uv run chat.py`. Real logic lives in gemma4_local.chat."""

import argparse
from pathlib import Path

from gemma4_local.chat import run
from gemma4_local.defaults import DEFAULTS
from gemma4_local.model import resolve
from gemma4_local.session import Sampler

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Chat with Gemma 4 via MLX.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--model", default=DEFAULTS["model_id"], help="HF id or alias")
    parser.add_argument("--temperature", type=float, default=DEFAULTS["temperature"], help="sampling temperature")
    parser.add_argument("--top-p", type=float, default=DEFAULTS["top_p"], help="nucleus sampling cutoff")
    parser.add_argument("--max-tokens", type=int, default=DEFAULTS["max_tokens"], help="max tokens per reply")
    parser.add_argument(
        "--sessions-dir", type=Path, default=Path(DEFAULTS["sessions_dir"]), help="where /save writes session JSON"
    )
    system_group = parser.add_mutually_exclusive_group()
    system_group.add_argument("--system", help="system prompt text")
    system_group.add_argument("--system-file", type=Path, help="path to a file containing the system prompt")
    args = parser.parse_args()

    sampler = Sampler(
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
    )
    if args.system_file is not None:
        system_prompt = args.system_file.read_text(encoding="utf-8")
    else:
        system_prompt = args.system
    run(resolve(args.model), sampler, args.sessions_dir, system_prompt)
