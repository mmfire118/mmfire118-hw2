import json


def test_extremely_large_input_can_trigger_resource_exhaustion(client):
    # Construct a very large binary string; app does int(value, 2) with no limits
    # WARNING IF YOU MAKE THIS TOO LARGE IT WILL JUST CRASH THE SERVER e.g. 2000000000000000000000 AS PYTEST IS KILLED BY THE OS `zsh: killed     pytest -q`
    large_binary = "1" * 200000  # 200k bits ~ 60KB string; conversion can be expensive
    resp = client.post(
        "/convert",
        data=json.dumps({"input": large_binary, "inputType": "binary", "outputType": "decimal"}),
        content_type="application/json",
    )
    # Expect server to reject or limit; current app likely processes it (or times out elsewhere)
    # We assert a 413/400 style response; test will fail if 200
    assert resp.status_code in (400, 413)


