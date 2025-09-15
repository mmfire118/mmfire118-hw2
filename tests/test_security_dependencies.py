from pathlib import Path


def parse_requirements_versions():
    req = Path("requirements.txt").read_text().splitlines()
    versions = {}
    for line in req:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" in line:
            name, ver = line.split("==", 1)
            versions[name.strip()] = ver.strip()
    return versions


def test_flask_version_not_vulnerable():
    # See: Flask 3.0.3 vulnerabilities (fixes available)
    # https://secure.software/pypi/packages/flask/vulnerabilities/3.0.3
    versions = parse_requirements_versions()
    assert "Flask" in versions
    # Expect not to pin a known vulnerable version
    assert versions["Flask"] != "3.0.3"


