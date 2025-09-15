import base64
import json


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


def test_zero_base64_encoding_explicit_zero_length(client):
    # Expect zero to have a non-empty base64 representation (e.g., single zero byte)
    data = post_convert(client, "0", "decimal", "base64")
    assert data["error"] is None
    assert data["result"] != ""


def test_base64_little_vs_big_endian_mismatch(client):
    # App uses big-endian; the spec we test elsewhere assumes little-endian
    number = 0x0102
    # Big-endian bytes -> b"\x01\x02"
    big = base64.b64encode((number).to_bytes(2, "big")).decode()
    little = base64.b64encode((number).to_bytes(2, "little")).decode()

    # decimal -> base64 matches big-endian
    d2b = post_convert(client, str(number), "decimal", "base64")
    assert d2b["error"] is None
    assert d2b["result"] == big
    assert d2b["result"] != little


def test_negative_decimal_to_base64_should_work(client):
    # Expect app to support negative numbers or define a clear policy
    data = post_convert(client, "-42", "decimal", "base64")
    # Chosen expectation: should succeed with a non-empty base64 string
    assert data["error"] is None
    assert isinstance(data["result"], str)
    assert data["result"] != ""


def test_empty_base64_input_decodes_to_zero(client):
    # Exploit: empty base64 string is accepted and coerces to decimal 0
    data = post_convert(client, "", "base64", "decimal")
    assert data["error"] is None
    assert data["result"] == "0"


def test_non_strict_base64_accepts_garbage(client):
    # 'AAE=' decodes to b"\x00\x01". With garbage appended, library ignores invalid chars.
    payload = "AAE=<>notbase64!!"
    data = post_convert(client, payload, "base64", "decimal")
    # Expect strict rejection, but app accepts and decodes, demonstrating leniency exploit
    assert data["error"] is None
    assert data["result"] == str(int.from_bytes(b"\x00\x01", "big"))


