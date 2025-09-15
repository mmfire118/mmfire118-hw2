import re


def get_home_html(client) -> str:
    resp = client.get("/")
    assert resp.status_code == 200
    return resp.data.decode("utf-8", errors="ignore")


def test_main_landmark_present(client):
    html = get_home_html(client)
    # Expect either a <main> element or role="main"
    assert ("<main" in html.lower()) or ("role=\"main\"" in html.lower())


def test_header_nav_footer_landmarks_present(client):
    html = get_home_html(client).lower()
    # Expect semantic landmarks for structure/navigation
    assert "<header" in html
    assert "<nav" in html
    assert "<footer" in html


def _hex_to_rgb(hex_color: str):
    hex_color = hex_color.strip().lower()
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]
    if len(hex_color) == 3:
        hex_color = "".join(c*2 for c in hex_color)
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def _srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _relative_luminance(rgb):
    r, g, b = rgb
    R = _srgb_to_linear(r)
    G = _srgb_to_linear(g)
    B = _srgb_to_linear(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def _contrast_ratio(fg_rgb, bg_rgb):
    L1 = _relative_luminance(fg_rgb)
    L2 = _relative_luminance(bg_rgb)
    light = max(L1, L2)
    dark = min(L1, L2)
    return (light + 0.05) / (dark + 0.05)


def test_button_text_contrast_meets_wcag(client):
    html = get_home_html(client)
    # Extract inline CSS for button
    # Rough parse: find 'button { ... }' block and read background-color and color
    m = re.search(r"button\s*\{([^}]*)\}", html, flags=re.IGNORECASE | re.DOTALL)
    assert m, "No <button> CSS block found"
    block = m.group(1)

    # Defaults if not found
    fg = None
    bg = None

    col_m = re.search(r"color\s*:\s*([^;]+);", block, flags=re.IGNORECASE)
    if col_m:
        fg_val = col_m.group(1).strip()
        fg = _hex_to_rgb("#ffffff" if fg_val.lower() == "white" else fg_val)

    bg_m = re.search(r"background-color\s*:\s*([^;]+);", block, flags=re.IGNORECASE)
    if bg_m:
        bg_val = bg_m.group(1).strip()
        # Common named color
        if bg_val.lower() == "white":
            bg = _hex_to_rgb("#ffffff")
        else:
            bg = _hex_to_rgb(bg_val)

    # If button background-color not specified, try to derive actual page background from body
    if bg is None:
        body_m = re.search(r"body\s*\{([^}]*)\}", html, flags=re.IGNORECASE | re.DOTALL)
        if body_m:
            body_block = body_m.group(1)
            body_bg_m = re.search(r"background-color\s*:\s*([^;]+);", body_block, flags=re.IGNORECASE)
            if body_bg_m:
                body_bg_val = body_bg_m.group(1).strip()
                if body_bg_val.lower() == "white":
                    bg = _hex_to_rgb("#ffffff")
                else:
                    bg = _hex_to_rgb(body_bg_val)
    # Final fallback to white if still unknown
    if bg is None:
        bg = _hex_to_rgb("#ffffff")
    if fg is None:
        fg = _hex_to_rgb("#000000")

    ratio = _contrast_ratio(fg, bg)
    # WCAG AA for normal text requires >= 4.5:1
    assert ratio >= 4.5


