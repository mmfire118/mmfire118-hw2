import json


def test_non_json_payload_should_be_400(client):
    resp = client.post("/convert", data="not-json", content_type="text/plain")
    # Expect a 4xx rather than 200
    assert resp.status_code >= 400
    # If JSON not returned, at least confirm not 200


def test_empty_json_should_be_400(client):
    resp = client.post("/convert", data=json.dumps({}), content_type="application/json")
    # Expect a 4xx rather than 200
    assert resp.status_code >= 400
    data = resp.get_json()
    assert data["result"] is None
    assert isinstance(data["error"], str)


def test_error_message_should_be_generic(client):
    # Trigger an error (invalid hex char)
    resp = client.post(
        "/convert",
        data=json.dumps({"input": "g", "inputType": "hexadecimal", "outputType": "decimal"}),
        content_type="application/json",
    )
    assert resp.status_code == 200  # current behavior
    data = resp.get_json()
    assert data["result"] is None
    # Expect a generic message, but app currently returns raw exception text
    assert data["error"] in ("Invalid input", "Bad Request")


def test_malformed_json_body_returns_useful_error(client):
    # Send broken JSON that Flask will parse as data but not JSON
    resp = client.post(
        "/convert",
        data="{\"input\": 42, \"inputType\": decimal, \"outputType\": binary}",
        content_type="application/json",
    )
    # Expect a 4xx with a controlled message; app likely returns 200 and generic error
    assert resp.status_code >= 400


