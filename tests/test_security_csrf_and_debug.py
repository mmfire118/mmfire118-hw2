import json


def test_debug_flag_not_enabled_in_production(client):
    # Expect debug to be disabled (app.run(debug=True) is present in code)
    # We cannot run the server process here, but we can assert config
    from api.index import app

    assert not app.debug


def test_missing_csrf_protection_on_convert(client):
    # POST without CSRF token should be rejected for a state-changing endpoint
    resp = client.post(
        "/convert",
        data=json.dumps({"input": "42", "inputType": "decimal", "outputType": "binary"}),
        content_type="application/json",
    )
    # Expect 403 or similar when CSRF is enforced. The app currently allows it.
    assert resp.status_code in (400, 401, 403)


