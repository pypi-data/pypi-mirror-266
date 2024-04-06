from pathlib import Path


def filename(name: str) -> str:
    return Path(__file__).parent.joinpath(name).as_posix()


__all__ = ["filename"]
