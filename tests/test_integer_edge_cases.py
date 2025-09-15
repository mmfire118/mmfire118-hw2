import json


def test_leading_plus_sign_decimal_not_handled(client):
    # '+42' should be a valid decimal string; app int() can handle it, but include to document behavior
    data = json.dumps({"input": "+42", "inputType": "decimal", "outputType": "binary"})
    resp = client.post("/convert", data=data, content_type="application/json")
    res = resp.get_json()
    # Expect success (documenting), but if behavior changes, this will flag
    assert res["error"] is None
    assert res["result"] == "101010"


def test_whitespace_only_input_accepted_as_error(client):
    # Whitespace-only input should be rejected, not crash or succeed
    data = json.dumps({"input": "   ", "inputType": "decimal", "outputType": "binary"})
    resp = client.post("/convert", data=data, content_type="application/json")
    res = resp.get_json()
    assert res["result"] is None
    assert isinstance(res["error"], str)


