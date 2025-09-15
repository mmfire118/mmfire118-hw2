import ast
from pathlib import Path


def test_no_bare_except_clauses():
    src = Path("api/index.py").read_text()
    tree = ast.parse(src)
    bare_excepts = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            bare_excepts.append(node)

    # Expect no bare excepts; the app currently uses bare excepts in helpers
    assert not bare_excepts


