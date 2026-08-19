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
