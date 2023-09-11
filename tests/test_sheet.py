from nicesheet.sheet import extract_ref


def test_extract_ref():
    assert (None, "Test text") == extract_ref("Test text")
    assert ("1.4.2", "Test text") == extract_ref("(1.4.2) Test text")