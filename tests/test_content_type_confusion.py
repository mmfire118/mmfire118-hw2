import json


def test_json_with_text_plain_content_type_is_accepted(client):
    # Send valid JSON but wrong content-type; expect 415/400, app returns 200
    resp = client.post(
        "/convert",
        data=json.dumps({"input": "42", "inputType": "decimal", "outputType": "binary"}),
        content_type="text/plain",
    )
    assert resp.status_code >= 400


def test_text_body_with_application_json_content_type_is_accepted(client):
    # Send non-JSON body but with application/json; expect 4xx, app returns 200
    resp = client.post(
        "/convert",
        data="just some text not json",
        content_type="application/json",
    )
    assert resp.status_code >= 400


