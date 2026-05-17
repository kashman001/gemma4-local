"""Interactive chat REPL for Gemma 4 via MLX-LM."""

from datetime import datetime
from pathlib import Path
from time import perf_counter

from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler

from gemma4_local.model import resolve
from gemma4_local.session import Sampler, Session, load_session, save_session

HELP_TEXT = """\
/help         show this message
/reset        clear conversation history
/system <t>   set system prompt; /system alone clears it
/save [path]  save session to <sessions_dir>/<timestamp>.json or <path>
/load <path>  load a saved session
/model <id>   swap to a different model (alias or HF id)
/tokens       show timing/token metrics for the last response
exit          quit
"""


def run(
    model_id: str,
    sampler: Sampler,
    sessions_dir: Path,
    system_prompt: str | None,
) -> None:
    print(f"Loading {model_id} ...")
    model, tokenizer = load(model_id)
    mlx_sampler = make_sampler(temp=sampler.temperature, top_p=sampler.top_p)

    messages: list[dict[str, str]] = []
    last_metrics: dict[str, float] | None = None
    print("Ready. Type '/help' for commands, 'exit' to quit.\n")

    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user == "exit":
            break
        if user == "/help":
            print(HELP_TEXT)
            continue
        if user == "/reset":
            messages.clear()
            print("(history cleared)\n")
            continue
        if user == "/system":
            system_prompt = None
            print("(system prompt cleared)\n")
            continue
        if user.startswith("/system "):
            system_prompt = user[len("/system "):].strip()
            preview = system_prompt if len(system_prompt) <= 60 else system_prompt[:60] + "…"
            print(f"(system prompt set: {preview})\n")
            continue
        if user == "/tokens":
            if last_metrics is None:
                print("(no responses yet)\n")
            else:
                m = last_metrics
                print(
                    f"TTFT: {m['ttft_ms']:.1f} ms  |  tokens: {int(m['total_tokens'])}  |  "
                    f"decode: {m['decode_tps']:.1f} tok/s  |  total: {m['total_wall_ms']:.1f} ms\n"
                )
            continue
        if user == "/model" or user == "/load":
            print(f"(usage: {user} <arg>)\n")
            continue
        if user.startswith("/model "):
            new_model_id = resolve(user[len("/model "):].strip())
            print(f"Loading {new_model_id} ...")
            try:
                model, tokenizer = load(new_model_id)
            except Exception as e:
                print(f"(model swap failed: {type(e).__name__}: {e})\n")
                continue
            model_id = new_model_id
            print("(model swapped)\n")
            continue
        if user.startswith("/load "):
            path = Path(user[len("/load "):].strip())
            try:
                loaded = load_session(path)
            except Exception as e:
                print(f"(load failed: {type(e).__name__}: {e})\n")
                continue
            if loaded.model_id != model_id:
                try:
                    confirm = input(
                        f"Saved session uses {loaded.model_id}; current is {model_id}. Swap? [y/N] "
                    ).strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print()
                    confirm = "n"
                if confirm != "y":
                    print("(load aborted)\n")
                    continue
                print(f"Loading {loaded.model_id} ...")
                try:
                    model, tokenizer = load(loaded.model_id)
                except Exception as e:
                    print(f"(model swap failed: {type(e).__name__}: {e})\n")
                    continue
                model_id = loaded.model_id
            sampler = loaded.sampler
            mlx_sampler = make_sampler(temp=sampler.temperature, top_p=sampler.top_p)
            system_prompt = loaded.system_prompt
            messages.clear()
            messages.extend(loaded.messages)
            print(f"(loaded {path}: {len(messages)} messages)\n")
            continue
        if user == "/save" or user.startswith("/save "):
            if user == "/save":
                ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
                path = sessions_dir / f"{ts}.json"
            else:
                path = Path(user[len("/save "):].strip())
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                save_session(
                    Session(
                        model_id=model_id,
                        system_prompt=system_prompt,
                        sampler=sampler,
                        messages=messages,
                    ),
                    path,
                )
                print(f"(saved to {path})\n")
            except Exception as e:
                print(f"(save failed: {type(e).__name__}: {e})\n")
            continue

        messages.append({"role": "user", "content": user})
        if system_prompt is not None:
            template_messages = [{"role": "system", "content": system_prompt}, *messages]
        else:
            template_messages = messages
        prompt = tokenizer.apply_chat_template(
            template_messages, add_generation_prompt=True, tokenize=False
        )

        print("gemma> ", end="", flush=True)
        reply_parts: list[str] = []
        t_start = perf_counter()
        t_first: float | None = None
        generation_tokens = 0
        for chunk in stream_generate(
            model, tokenizer, prompt, max_tokens=sampler.max_tokens, sampler=mlx_sampler
        ):
            if t_first is None:
                t_first = perf_counter()
            print(chunk.text, end="", flush=True)
            reply_parts.append(chunk.text)
            generation_tokens = chunk.generation_tokens
        t_end = perf_counter()
        print("\n")
        messages.append({"role": "assistant", "content": "".join(reply_parts)})

        if t_first is None:
            t_first = t_end
        last_metrics = {
            "ttft_ms": (t_first - t_start) * 1000,
            "total_tokens": generation_tokens,
            "decode_tps": generation_tokens / max(t_end - t_first, 1e-9),
            "total_wall_ms": (t_end - t_start) * 1000,
        }
