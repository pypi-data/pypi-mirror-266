import json
from pathlib import Path

from walk import walk_repository

if __name__ == "__main__":
    directory = Path("/Users/manuel/PycharmProjects/shading")
    with open("/Users/manuel/PycharmProjects/ast-walker/repository_info.json", "w") as f:
        f.write(json.dumps(walk_repository(directory)))
