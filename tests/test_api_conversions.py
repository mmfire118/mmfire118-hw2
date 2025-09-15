import base64
import itertools
import json
import math
import pytest


ALL_TYPES = [
    "text",
    "binary",
    "octal",
    "decimal",
    "hexadecimal",
    "base64",
]


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
    # For stricter behavior, expect 200 only on success and 4xx on error.
    # The current app returns 200 always; individual tests will assert expectations.
    data = resp.get_json()
    assert set(data.keys()) == {"result", "error"}
    return data


@pytest.mark.parametrize(
    "number",
    [0, 1, 2, 7, 8, 15, 16, 42, 255, 256, 1024, 65535, 65536],
)
@pytest.mark.parametrize("output_type", ALL_TYPES)
def test_decimal_to_all_outputs(client, number, output_type):
    data = post_convert(client, str(number), "decimal", output_type)
    assert data["error"] is None
    # Basic shape: non-empty string for non-zero conversions, '0' for zero in bases
    assert isinstance(data["result"], str)
    if output_type in {"binary", "octal", "hexadecimal"}:
        if number == 0:
            assert data["result"] == "0"
        else:
            assert len(data["result"]) >= 1


@pytest.mark.parametrize(
    "text,expected",
    [
        ("zero", 0),
        ("nil", 0),
        ("one", 1),
        ("two", 2),
        ("ten", 10),
        ("One", 1),
        ("THREE", 3),
        ("three!", 3),
    ],
)
@pytest.mark.parametrize("output_type", ["binary", "octal", "decimal", "hexadecimal", "text", "base64"])
def test_text_to_all_outputs(client, text, expected, output_type):
    data = post_convert(client, text, "text", output_type)
    assert data["error"] is None
    if output_type == "decimal":
        assert data["result"] == str(expected)
    elif output_type == "binary":
        assert data["result"] == bin(expected)[2:]
    elif output_type == "octal":
        assert data["result"] == oct(expected)[2:]
    elif output_type == "hexadecimal":
        assert data["result"] == hex(expected)[2:]
    elif output_type == "text":
        # num2words can return hyphenated/space text; just check it's a string
        assert isinstance(data["result"], str)
        assert len(data["result"]) > 0
    elif output_type == "base64":
        # Little-endian expected
        byte_count = (expected.bit_length() + 7) // 8
        expected_bytes = expected.to_bytes(byte_count, byteorder="little")
        assert data["result"] == base64.b64encode(expected_bytes).decode("utf-8")


@pytest.mark.parametrize(
    "number",
    [0, 1, 2, 7, 8, 15, 16, 42, 255, 256, 1024, 65535, 65536],
)
def test_binary_octal_hex_to_decimal_roundtrip(client, number):
    # binary -> decimal
    data_b = post_convert(client, bin(number)[2:], "binary", "decimal")
    assert data_b["error"] is None
    assert int(data_b["result"]) == number

    # octal -> decimal
    data_o = post_convert(client, oct(number)[2:], "octal", "decimal")
    assert data_o["error"] is None
    assert int(data_o["result"]) == number

    # hex -> decimal
    data_h = post_convert(client, hex(number)[2:], "hexadecimal", "decimal")
    assert data_h["error"] is None
    assert int(data_h["result"]) == number


@pytest.mark.parametrize("number", [0, 1, 2, 15, 16, 42, 255, 256, 4096])
def test_base64_roundtrip_little_endian(client, number):
    # decimal -> base64
    data_to_b64 = post_convert(client, str(number), "decimal", "base64")
    assert data_to_b64["error"] is None

    # Build expected using little-endian
    byte_count = (number.bit_length() + 7) // 8
    expected_bytes = number.to_bytes(byte_count, byteorder="little")
    expected_b64 = base64.b64encode(expected_bytes).decode("utf-8")
    assert data_to_b64["result"] == expected_b64

    # base64 -> decimal
    data_from_b64 = post_convert(client, expected_b64, "base64", "decimal")
    assert data_from_b64["error"] is None
    assert int(data_from_b64["result"]) == number


@pytest.mark.parametrize(
    "input_value,input_type",
    [
        ("102", "binary"),  # invalid binary
        ("89", "octal"),  # invalid octal
        ("not-a-number", "decimal"),
        ("g", "hexadecimal"),
        ("**", "base64"),
        ("eleventy", "text"),  # unsupported word
    ],
)
def test_invalid_inputs_return_error(client, input_value, input_type):
    data = post_convert(client, input_value, input_type, "decimal")
    assert data["result"] is None
    assert isinstance(data["error"], str)
    assert len(data["error"]) > 0


@pytest.mark.parametrize(
    "value,base,expected",
    [
        ("0b101010", "binary", 42),
        ("0o52", "octal", 42),
        ("0x2a", "hexadecimal", 42),
    ],
)
def test_prefixed_literals_should_work(client, value, base, expected):
    data = post_convert(client, value, base, "decimal")
    # Expect success for common prefixed literals
    assert data["error"] is None
    assert data["result"] == str(expected)


@pytest.mark.parametrize(
    "field,value",
    [
        ("inputType", "unknown"),
        ("outputType", "unknown"),
    ],
)
def test_invalid_types_return_error(client, field, value):
    payload = {
        "input": "1",
        "inputType": "decimal",
        "outputType": "decimal",
    }
    payload[field] = value
    data = post_convert(client, payload["input"], payload["inputType"], payload["outputType"]) if field == "noop" else client.post(
        "/convert",
        data=json.dumps(payload),
        content_type="application/json",
    ).get_json()
    assert data["result"] is None
    assert isinstance(data["error"], str)


def test_missing_fields_return_error(client):
    # Missing outputType
    resp = client.post(
        "/convert",
        data=json.dumps({"input": "1", "inputType": "decimal"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["result"] is None
    assert isinstance(data["error"], str)


def test_homepage_serves_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Numeric Converter" in resp.data


