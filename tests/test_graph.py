import pytest

from src.graph import hard_validate_citations, _safe_json_loads, _extract_doc_ids


def test_should_return_no_issues_when_all_bullets_have_valid_citations():
    # Arrange
    draft = "- Some claim supported by evidence. [DOC:S1]"
    allowed_docs = ["S1", "S2"]

    # Act
    actual = hard_validate_citations(draft, allowed_docs)

    # Assert
    assert actual == []


def test_should_flag_issue_when_bullet_line_has_no_citation():
    # Arrange
    draft = "- This claim has no citation at all"
    allowed_docs = ["S1"]

    # Act
    actual = hard_validate_citations(draft, allowed_docs)

    # Assert
    assert len(actual) == 1
    assert actual[0]["reason"] == "Missing [DOC:...] citation"


def test_should_flag_issue_when_bullet_cites_unknown_doc_id():
    # Arrange
    draft = "- Claim with invalid reference [DOC:S99]"
    allowed_docs = ["S1", "S2"]

    # Act
    actual = hard_validate_citations(draft, allowed_docs)

    # Assert
    assert len(actual) == 1
    assert "S99" in actual[0]["reason"]


def test_should_return_no_issues_when_draft_has_no_bullet_lines():
    # Arrange
    draft = "## Background\nSome paragraph without bullets."
    allowed_docs = ["S1"]

    # Act
    actual = hard_validate_citations(draft, allowed_docs)

    # Assert
    assert actual == []


def test_should_return_no_issues_when_draft_is_empty():
    # Act
    actual = hard_validate_citations("", ["S1"])

    # Assert
    assert actual == []


def test_should_parse_valid_json_string():
    # Arrange
    raw = '{"key": "value", "number": 42}'

    # Act
    actual = _safe_json_loads(raw)

    # Assert
    assert actual == {"key": "value", "number": 42}


def test_should_parse_json_when_surrounded_by_extra_text():
    # Arrange
    raw = 'Here is the result: {"key": "value"} as requested.'

    # Act
    actual = _safe_json_loads(raw)

    # Assert
    assert actual == {"key": "value"}


def test_should_raise_when_string_contains_no_json():
    # Arrange
    raw = "no json here at all"

    # Act / Assert
    with pytest.raises(Exception):
        _safe_json_loads(raw)


def test_should_return_empty_list_when_text_has_no_doc_ids():
    # Arrange
    text = "A draft with no citations."

    # Act
    actual = _extract_doc_ids(text)

    # Assert
    assert actual == []


def test_should_extract_all_doc_ids_from_text():
    # Arrange
    text = "Evidence from [DOC:S1] and also [DOC:S3]."

    # Act
    actual = _extract_doc_ids(text)

    # Assert
    assert actual == ["S1", "S3"]


def test_should_deduplicate_doc_ids_when_same_id_appears_multiple_times():
    # Arrange
    text = "[DOC:S1] repeated claim [DOC:S1] and [DOC:S2]."

    # Act
    actual = _extract_doc_ids(text)

    # Assert
    assert actual == ["S1", "S2"]
