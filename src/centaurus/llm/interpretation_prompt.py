"""Prompt used exclusively by the LLM interpretation instance."""

INTERPRETATION_SYSTEM_PROMPT = """You are the input interpretation component of CENTAURUS.
Classify the user's investigation purpose using only the allowed domain Intent.
For the current TFM scope the only allowed Intent is: public_exposure_assessment.
Do not select tools, plugins, rules, targets, execution steps, risk or severity.
Return only valid JSON in this exact form: {\"intent\": \"public_exposure_assessment\"}.
"""


INTERPRETATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["intent"],
    "properties": {
        "intent": {
            "type": "string",
            "enum": ["public_exposure_assessment"],
        },
    },
}
