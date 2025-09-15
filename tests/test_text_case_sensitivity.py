import json


def test_text_mixed_case_and_punctuation_should_work(client):
    # App strips non-letters and lowercases; ensure mixed-case with punctuation is handled
    resp = client.post(
        "/convert",
        data=json.dumps({"input": "One, Hundred!", "inputType": "text", "outputType": "decimal"}),
        content_type="application/json",
    )
    data = resp.get_json()
    # Expect broader support (will currently fail)
    assert data["error"] is None
    assert data["result"] == "100"


