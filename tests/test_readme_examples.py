import json
from num2words import num2words


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


def test_readme_decimal_to_binary_42(client):
    data = post_convert(client, "42", "decimal", "binary")
    assert data["error"] is None
    assert data["result"] == "101010"


def test_readme_text_to_decimal_forty_two(client):
    data = post_convert(client, "forty two", "text", "decimal")
    # Expect support per README
    assert data["error"] is None
    assert data["result"] == "42"


def test_readme_hex_to_text_2a(client):
    data = post_convert(client, "2a", "hexadecimal", "text")
    assert data["error"] is None
    assert data["result"] == num2words(42)


