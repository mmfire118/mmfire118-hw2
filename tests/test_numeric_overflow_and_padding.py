import base64
import json


def test_base64_strips_leading_zero_bytes_changes_value(client):
    # Decimal 1 as two bytes with leading zero differs by encoding choice
    b = b"\x00\x01"
    b64 = base64.b64encode(b).decode()
    # App decodes to int and re-encodes without preserving padding
    to_dec = client.post(
        "/convert",
        data=json.dumps({"input": b64, "inputType": "base64", "outputType": "decimal"}),
        content_type="application/json",
    ).get_json()
    assert to_dec["error"] is None
    assert to_dec["result"] == "1"

    # Now back to base64
    to_b64 = client.post(
        "/convert",
        data=json.dumps({"input": to_dec["result"], "inputType": "decimal", "outputType": "base64"}),
        content_type="application/json",
    ).get_json()
    assert to_b64["error"] is None
    # Leading zero byte is lost; round-trip does not preserve original base64
    assert to_b64["result"] != b64


