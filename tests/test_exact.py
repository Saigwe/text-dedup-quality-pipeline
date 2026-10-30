from dedup.exact import exact_dedup


def test_exact_dedup_ignores_case_and_whitespace():
    kept, removed = exact_dedup(["Hello  World", "hello world", "Other text"])
    assert kept == ["Hello  World", "Other text"]
    assert removed == [1]
