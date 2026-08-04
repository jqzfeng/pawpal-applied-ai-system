from ai_assistant import answer_question, build_prompt, check_guardrail, load_knowledge_base, retrieve_context


def fake_generator(prompt: str) -> str:
    return "Grounded test answer [1]."


def test_knowledge_base_has_required_records():
    records = load_knowledge_base()
    assert len(records) >= 8


def test_retrieves_feeding_context():
    results = retrieve_context("How often should I feed my adult dog?")
    assert results[0]["id"] == "feeding_schedule"


def test_retrieves_bathing_context():
    results = retrieve_context("How often should I bathe and groom my dog?")
    assert results[0]["id"] == "bathing_grooming"


def test_emergency_guardrail_bypasses_generator():
    called = False

    def should_not_run(_prompt):
        nonlocal called
        called = True

    result = answer_question("My dog cannot breathe", generator=should_not_run)
    assert result["status"] == "emergency"
    assert called is False


def test_medication_guardrail():
    result = answer_question("Should I double the medication dose?", generator=fake_generator)
    assert result["status"] == "medication_safety"


def test_empty_input():
    assert check_guardrail("   ")["status"] == "error"


def test_unsupported_species():
    result = answer_question("How should I feed my iguana?", generator=fake_generator)
    assert result["status"] == "unsupported_species"


def test_missing_context_does_not_call_model():
    result = answer_question("What color leash looks fashionable?", generator=fake_generator)
    assert result["status"] == "insufficient_context"


def test_success_returns_sources_and_uses_profile():
    captured = {}

    def capture(prompt):
        captured["prompt"] = prompt
        return "Senior dogs may benefit from shorter activity sessions [1]."

    result = answer_question(
        "How much exercise does my senior dog need?",
        {"name": "Mochi", "life stage": "Senior"},
        generator=capture,
    )
    assert result["status"] == "ok"
    assert result["sources"]
    assert "Mochi" in captured["prompt"]
    assert "Retrieved evidence" in captured["prompt"]


def test_generation_error_is_handled():
    def broken_generator(_prompt):
        raise RuntimeError("test failure")

    result = answer_question("How often should I brush my dog?", generator=broken_generator)
    assert result["status"] == "generation_error"
