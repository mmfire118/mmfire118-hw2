import json
import pytest


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


@pytest.mark.parametrize("number", [-1, -2, -15, -16, -42, -255, -256])
@pytest.mark.parametrize("output_type", ["binary", "octal", "hexadecimal"]) 
def test_negative_to_non_decimal_outputs(client, number, output_type):
    # The current app uses bin/oct/hex on negatives which yields '-0b..' style
    data = post_convert(client, str(number), "decimal", output_type)
    # For an app expecting unsigned representations, this is likely undesirable;
    # ensure the behavior is at least surfaced (should not be an error)
    assert data["error"] is None
    assert isinstance(data["result"], str)
    assert data["result"].startswith("-")


