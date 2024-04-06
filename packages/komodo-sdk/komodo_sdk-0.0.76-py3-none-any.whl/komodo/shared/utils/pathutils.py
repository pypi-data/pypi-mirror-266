import os
from pathlib import Path


def find_nearest_parent_containing(name: str):
    candidate = Path(os.getcwd())
    while candidate != Path("/"):
        if (candidate / name).exists():
            return candidate
        candidate = candidate.parent
    return None
