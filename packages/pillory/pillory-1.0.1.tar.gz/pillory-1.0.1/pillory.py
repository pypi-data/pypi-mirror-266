"""
A linter to scrutinize how you are using mocks in Python.
"""

__version__ = "1.0.1"

import ast
import importlib
import pathlib
import sys
from collections.abc import Iterator

# Excludes taken from ruff.
EXCLUDE = [
    ".bzr",
    ".direnv",
    ".eggs",
    ".git",
    ".git-rewrite",
    ".hg",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".nox",
    ".pants.d",
    ".pyenv",
    ".pytest_cache",
    ".pytype",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    ".vscode",
    "__pypackages__",
    "_build",
    "buck-out",
    "build",
    "dist",
    "node_modules",
    "site-packages",
    "venv",
]


def walk_path(path: pathlib.Path) -> Iterator[pathlib.Path]:
    if path.is_dir() and str(path) not in EXCLUDE:
        for item in path.iterdir():
            yield from walk_path(item)
    else:
        yield path


class MockImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.patches = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "patch":
            self.patches.append(node)


def import_or_getattr(target, current=None):
    if "." in target:
        first, rest = target.split(".", 1)
    else:
        first = target
        rest = None
    try:
        found = getattr(current, first)
    except AttributeError:
        if not current:
            found = importlib.import_module(first)
        else:
            found = importlib.import_module(f"{current.__name__}.{first}")
    if rest:
        return import_or_getattr(rest, current=found)
    return found


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != ".":
        starting_files = list(pathlib.Path(".").glob(sys.argv[1]))
    else:
        starting_files = [pathlib.Path(".")]
    files = [file for path in starting_files for file in walk_path(path)]
    for file in files:
        try:
            source = file.read_text()
            parsed = ast.parse(source, filename=str(file))
        except Exception:
            continue
        visitor = MockImportVisitor()
        visitor.visit(parsed)
        for node in visitor.patches:
            arg = node.args[0].value
            target, attribute = arg.rsplit(".", 1)
            if target == "builtins":
                print(
                    f"{str(file)}:{node.lineno}:{node.col_offset}: PM103 patched builtins instead of module under test {arg}"
                )
            module = import_or_getattr(target)
            patched = getattr(module, attribute)
            if not hasattr(patched, "__module__"):
                print(
                    f"{str(file)}:{node.lineno}:{node.col_offset}: PM102 patched is not a top level module attribute {arg}"
                )
            elif patched.__module__ == target:
                print(
                    f"{str(file)}:{node.lineno}:{node.col_offset}: PM101 patched implementation of {arg}"
                )
