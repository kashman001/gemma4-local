import pytest

from gemma4_local.model import resolve


@pytest.mark.parametrize(
    "alias,expected",
    [
        ("31b", "mlx-community/gemma-4-31B-it-OptiQ-4bit"),
        ("26b", "mlx-community/gemma-4-26b-a4b-it-4bit"),
    ],
)
def test_known_alias_resolves(alias, expected):
    assert resolve(alias) == expected


def test_full_hf_id_passes_through():
    assert resolve("mlx-community/some-other-org-model") == "mlx-community/some-other-org-model"


def test_unknown_short_string_passes_through():
    assert resolve("not-a-known-alias-xyz") == "not-a-known-alias-xyz"
