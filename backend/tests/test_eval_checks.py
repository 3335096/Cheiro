from evals.run_eval import evaluate

SOURCES = [{"title": "Cheiro's Language of the Hand", "chunk_index": 3}]


def test_passes_when_expectations_are_met():
    case = {
        "expected_source_titles": ["Cheiro's Language of the Hand"],
        "must_include": ["life line"],
        "must_not_include": ["diagnosis"],
    }

    checks = evaluate(case, "The Life Line shows vitality.", SOURCES)

    assert all(checks.values())


def test_fails_on_missing_source_missing_phrase_and_forbidden_phrase():
    case = {
        "expected_source_titles": ["Another Book"],
        "must_include": ["fate line"],
        "must_not_include": ["diagnosis"],
    }

    checks = evaluate(case, "This is a medical Diagnosis.", SOURCES)

    assert checks == {"cited": True, "retrieval": False, "include": False, "exclude": False}


def test_answer_without_sources_is_not_cited():
    assert evaluate({}, "Some answer", [])["cited"] is False
