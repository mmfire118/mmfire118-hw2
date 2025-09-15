import ast
from pathlib import Path


def test_text2digits_import_is_used():
    src = Path("api/index.py").read_text()
    tree = ast.parse(src)

    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "text2digits":
            for alias in node.names:
                imported_names.add(alias.asname or alias.name)

    assert "text2digits" in imported_names, "text2digits is not imported as expected"

    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)

    # Expect the imported symbol to be referenced somewhere in the module
    assert (
        "text2digits" in used_names
    ), "Imported symbol 'text2digits' is unused in api/index.py"


