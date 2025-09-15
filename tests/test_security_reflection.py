import json


def test_error_reflects_user_input_in_message(client):
    # Payload with script tag to demonstrate reflection in server error message
    payload = {
        "input": "g</script><script>alert('xss')</script>",
        "inputType": "hexadecimal",
        "outputType": "decimal",
    }
    resp = client.post(
        "/convert",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["result"] is None
    # Server returns raw exception text containing the tainted input
    assert "<script>alert('xss')</script>" in data["error"]


