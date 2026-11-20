from pathlib import Path


def read_secret(path: str):
    secret_path = Path("../secrets") / path
    with secret_path.open("r") as fd:
        value = fd.read()

    return value
