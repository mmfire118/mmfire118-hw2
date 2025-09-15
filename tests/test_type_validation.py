import json


def test_hexadecimal_input_must_be_string_not_number(client):
    # Send numeric JSON for hex input. App will 200 with error text; expect 4xx.
    resp = client.post(
        "/convert",
        data=json.dumps({"input": 42, "inputType": "hexadecimal", "outputType": "decimal"}),
        content_type="application/json",
    )
    assert resp.status_code >= 400


def test_binary_input_with_spaces_should_be_rejected(client):
    # '1010 10' contains a space; int(value, 2) should reject, but server may coerce oddly if sanitized earlier
    resp = client.post(
        "/convert",
        data=json.dumps({"input": "1010 10", "inputType": "binary", "outputType": "decimal"}),
        content_type="application/json",
    )
    # Expect a 4xx policy; app returns 200 with error string
    assert resp.status_code >= 400


