import json


def test_binary_input_with_0b_prefix_should_work(client):
    resp = client.post(
        "/convert",
        data=json.dumps({"input": "0b101010", "inputType": "binary", "outputType": "decimal"}),
        content_type="application/json",
    )
    data = resp.get_json()
    # Expect success; app will likely error (invalid literal for int with base 2)
    assert data["error"] is None
    assert data["result"] == "42"


def test_octal_input_with_0o_prefix_should_work(client):
    resp = client.post(
        "/convert",
        data=json.dumps({"input": "0o52", "inputType": "octal", "outputType": "decimal"}),
        content_type="application/json",
    )
    data = resp.get_json()
    assert data["error"] is None
    assert data["result"] == "42"


def test_hex_input_with_0x_prefix_should_work(client):
    resp = client.post(
        "/convert",
        data=json.dumps({"input": "0x2a", "inputType": "hexadecimal", "outputType": "decimal"}),
        content_type="application/json",
    )
    data = resp.get_json()
    assert data["error"] is None
    assert data["result"] == "42"


