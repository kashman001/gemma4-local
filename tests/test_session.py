"""Tests for gemma4_local.session."""

import json

import pytest

from gemma4_local.session import (
    Sampler,
    Session,
    SessionSchemaError,
    load_session,
    save_session,
)


def test_roundtrip_full_session(tmp_path):
    session = Session(
        model_id="mlx-community/gemma-4-31B-it-OptiQ-4bit",
        system_prompt="You are a helpful assistant.",
        sampler=Sampler(temperature=0.3, top_p=0.85, max_tokens=512),
        messages=[
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi there"},
            {"role": "user", "content": "how are you?"},
        ],
    )
    path = tmp_path / "session.json"
    save_session(session, path)
    loaded = load_session(path)
    assert loaded == session


def test_roundtrip_null_system_prompt(tmp_path):
    session = Session(
        model_id="mlx-community/gemma-4-31B-it-OptiQ-4bit",
        system_prompt=None,
        sampler=Sampler(temperature=0.7, top_p=0.9, max_tokens=1024),
        messages=[{"role": "user", "content": "ping"}],
    )
    path = tmp_path / "session.json"
    save_session(session, path)
    loaded = load_session(path)
    assert loaded == session


def test_unknown_schema_version_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "999",
                "model_id": "x",
                "system_prompt": None,
                "sampler": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 1024},
                "messages": [],
            }
        )
    )
    with pytest.raises(SessionSchemaError) as exc_info:
        load_session(path)
    assert "999" in str(exc_info.value)
    assert str(path) in str(exc_info.value)


def test_missing_schema_version_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps(
            {
                "model_id": "x",
                "system_prompt": None,
                "sampler": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 1024},
                "messages": [],
            }
        )
    )
    with pytest.raises(SessionSchemaError) as exc_info:
        load_session(path)
    assert "missing" in str(exc_info.value)
    assert str(path) in str(exc_info.value)
