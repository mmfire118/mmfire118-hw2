def test_missing_basic_security_headers_on_home(client):
    resp = client.get("/")
    assert resp.status_code == 200
    # Expect common security headers to be present; app likely lacks them
    headers = resp.headers
    assert "Content-Security-Policy" in headers
    assert "X-Content-Type-Options" in headers and headers["X-Content-Type-Options"].lower() == "nosniff"
    assert "X-Frame-Options" in headers
    assert "Referrer-Policy" in headers
    assert "Permissions-Policy" in headers


