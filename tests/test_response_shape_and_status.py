import json


def test_response_always_contains_result_and_error(client):
    resp = client.post(
        "/convert",
        data=json.dumps({"input": "not-a-number", "inputType": "decimal", "outputType": "binary"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data.keys()) == {"result", "error"}


def test_success_should_have_200_error_should_have_4xx(client):
    # Assert policy that errors should not be 200, to flag current behavior
    bad = client.post(
        "/convert",
        data=json.dumps({"input": "g", "inputType": "hexadecimal", "outputType": "decimal"}),
        content_type="application/json",
    )
    assert bad.status_code >= 400


