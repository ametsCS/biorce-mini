from src.rag import _chunk_text, _extract_title


def test_should_return_empty_list_when_text_is_empty():
    # Act
    actual = _chunk_text("")

    # Assert
    assert actual == []


def test_should_return_single_chunk_when_text_fits_within_max_chars():
    # Arrange
    text = "short text"

    # Act
    actual = _chunk_text(text, max_chars=350)

    # Assert
    assert actual == ["short text"]


def test_should_split_into_multiple_chunks_when_text_exceeds_max_chars():
    # Arrange
    text = "a" * 400

    # Act
    actual = _chunk_text(text, max_chars=100, overlap=0)

    # Assert
    assert len(actual) > 1


def test_should_overlap_consecutive_chunks_when_overlap_is_set():
    # Arrange
    text = "abcdefghijklmnopqrstuvwxyz" * 20

    # Act
    actual = _chunk_text(text, max_chars=50, overlap=10)

    # Assert
    assert actual[1][:10] == actual[0][-10:]


def test_should_return_title_when_title_line_is_present():
    # Arrange
    raw = "TITLE: Asthma Biologics\nYEAR: 2023\nTEXT:\nsome content"

    # Act
    actual = _extract_title(raw, fallback="fallback")

    # Assert
    assert actual == "Asthma Biologics"


def test_should_return_fallback_when_no_title_line_present():
    # Arrange
    raw = "YEAR: 2023\nTEXT:\nsome content"

    # Act
    actual = _extract_title(raw, fallback="my_fallback")

    # Assert
    assert actual == "my_fallback"


def test_should_return_fallback_when_title_value_is_empty():
    # Arrange
    raw = "TITLE:\nYEAR: 2023\nTEXT:\nsome content"

    # Act
    actual = _extract_title(raw, fallback="my_fallback")

    # Assert
    assert actual == "my_fallback"


def test_should_be_case_insensitive_when_matching_title_line():
    # Arrange
    raw = "title: Lowercase Title\nTEXT:\ncontent"

    # Act
    actual = _extract_title(raw, fallback="fallback")

    # Assert
    assert actual == "Lowercase Title"
