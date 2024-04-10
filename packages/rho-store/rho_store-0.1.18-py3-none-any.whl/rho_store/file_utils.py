import os


def get_relative_path(path: str, caller_file: str) -> str:
    base_dir = os.path.dirname(caller_file)
    return os.path.join(base_dir, path)
