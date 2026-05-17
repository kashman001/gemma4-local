"""Session dataclasses and JSON persistence for the chat REPL."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

SCHEMA_VERSION = "1"


class SessionSchemaError(Exception):
    pass


@dataclass(frozen=True)
class Sampler:
    temperature: float
    top_p: float
    max_tokens: int


@dataclass(frozen=True)
class Metrics:
    ttft_ms: float
    decode_tps: float
    total_wall_ms: float
    peak_mem_gb: float


@dataclass(frozen=True)
class Session:
    model_id: str
    system_prompt: str | None
    sampler: Sampler
    messages: list[dict[str, str]]


def save_session(session: Session, path: Path) -> None:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "model_id": session.model_id,
        "system_prompt": session.system_prompt,
        "sampler": asdict(session.sampler),
        "messages": session.messages,
    }
    path.write_text(json.dumps(payload, indent=2))


def load_session(path: Path) -> Session:
    data = json.loads(path.read_text())
    version = data.get("schema_version")
    if version is None:
        raise SessionSchemaError(
            f"{path}: missing schema_version (expected {SCHEMA_VERSION!r})"
        )
    if version != SCHEMA_VERSION:
        raise SessionSchemaError(
            f"{path}: unknown schema_version {version!r} (expected {SCHEMA_VERSION!r})"
        )
    return Session(
        model_id=data["model_id"],
        system_prompt=data["system_prompt"],
        sampler=Sampler(**data["sampler"]),
        messages=data["messages"],
    )
