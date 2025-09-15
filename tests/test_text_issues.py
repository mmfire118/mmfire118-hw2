import json
import pytest


def post_convert(client, input_value, input_type, output_type):
    resp = client.post(
        "/convert",
        data=json.dumps({
            "input": input_value,
            "inputType": input_type,
            "outputType": output_type,
        }),
        content_type="application/json",
    )
    assert resp.status_code == 200
    return resp.get_json()


@pytest.mark.parametrize(
    "text,expected",
    [
        ("eleven", 11),
        ("twelve", 12),
        ("twenty one", 21),
        ("one hundred", 100),
        ("one hundred twenty three", 123),
        ("two thousand five", 2005),
    ],
)
def test_text_numbers_beyond_ten_should_work(client, text, expected):
    # Expect broader English number support to work
    data = post_convert(client, text, "text", "decimal")
    assert data["error"] is None
    assert data["result"] == str(expected)


def test_readme_example_forty_two_should_work(client):
    # README example says "forty two" works
    data = post_convert(client, "forty two", "text", "decimal")
    assert data["error"] is None
    assert data["result"] == "42"


@pytest.mark.parametrize(
    "raw,normalized,expected",
    [
        (" Twenty-One ", "twenty-one", 21),
        ("Twenty  One", "twenty  one", 21),
        ("twenty-one", "twenty-one", 21),
        ("one-hundred", "one-hundred", 100),
    ],
)
def test_hyphenated_and_whitespace_text_should_work(client, raw, normalized, expected):
    data = post_convert(client, raw, "text", "decimal")
    assert data["error"] is None
    assert data["result"] == str(expected)


