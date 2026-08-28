"""Tests for the versioned Ollama inference-profile contract."""

from dataclasses import FrozenInstanceError

import pytest

from centaurus.llm import (
    ANALYST_ASSISTANCE_INFERENCE_PROFILE,
    INTERPRETATION_INFERENCE_PROFILE,
    OllamaInferenceProfile,
)


def test_current_logical_llm_roles_use_separate_profile_instances():
    assert INTERPRETATION_INFERENCE_PROFILE is not ANALYST_ASSISTANCE_INFERENCE_PROFILE
    assert INTERPRETATION_INFERENCE_PROFILE == ANALYST_ASSISTANCE_INFERENCE_PROFILE


def test_current_qwen3_non_thinking_defaults_are_versioned():
    expected = OllamaInferenceProfile(
        think=False,
        temperature=0.7,
        top_p=0.8,
        top_k=20,
        min_p=0.0,
        seed=42,
    )

    assert INTERPRETATION_INFERENCE_PROFILE == expected
    assert ANALYST_ASSISTANCE_INFERENCE_PROFILE == expected
    assert expected.options() == {
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 20,
        "min_p": 0.0,
        "seed": 42,
    }


def test_inference_profile_is_immutable():
    profile = INTERPRETATION_INFERENCE_PROFILE

    with pytest.raises(FrozenInstanceError):
        profile.temperature = 0.1  # type: ignore[misc]


def test_inference_profile_adds_context_capacity_only_when_configured():
    profile = OllamaInferenceProfile(
        think=False,
        temperature=0.7,
        top_p=0.8,
        top_k=20,
        min_p=0.0,
        seed=42,
        num_ctx=8192,
        num_predict=1536,
    )

    options = profile.options()

    assert options["num_ctx"] == 8192
    assert options["num_predict"] == 1536
    assert "num_ctx" not in INTERPRETATION_INFERENCE_PROFILE.options()
    assert "num_predict" not in INTERPRETATION_INFERENCE_PROFILE.options()
