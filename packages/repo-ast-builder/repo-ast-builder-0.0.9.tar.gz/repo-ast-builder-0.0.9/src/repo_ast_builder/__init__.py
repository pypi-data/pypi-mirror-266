import json
from pathlib import Path

from repo_ast_builder.walk import walk_repository


def read_ast(path: str) -> str:
    return json.dumps(walk_repository(Path(path)))
