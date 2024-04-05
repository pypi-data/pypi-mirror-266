from __future__ import annotations

import json
import shutil
from os import environ
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

REPOSITORY = "https://raw.githubusercontent.com/charbonnierg/pytest-broadcaster"
REFERENCE = "main"
OUTPUT = "schemas"
SOURCES = Path(__file__).parent.parent.joinpath("src/schemas")


def replace_refs_and_ids(schema: dict[str, Any], ref_prefix: str) -> None:
    if "$ref" in schema:
        ref_template: str = schema["$ref"]
        ref_value = ref_template.split("/")[0]
        schema["$ref"] = f"{ref_prefix}/{ref_value}"
    if "$id" in schema:
        id_value = schema["$id"]
        schema["$id"] = f"{ref_prefix}/{id_value}"
    for value in schema.values():
        if isinstance(value, dict):
            replace_refs_and_ids(value, ref_prefix)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    replace_refs_and_ids(item, ref_prefix)


def create_schema(source: Path, output_directory: Path, ref_prefix: str) -> None:
    destination = output_directory.joinpath(source.name)
    content = json.loads(source.read_text())
    replace_refs_and_ids(content, ref_prefix)
    destination.write_text(json.dumps(content, indent=2))


def main(repository: str, reference: str, output_directory: str):
    # Validate reference and output
    if not (repository and reference and output_directory):
        raise ValueError("repository, reference and output_directory are required")
    if output_directory.startswith("/"):
        raise ValueError("output must be relative")
    if reference.startswith("/"):
        raise ValueError("reference cannot start with '/'")
    # Clean output directory
    destination = Path(output_directory)
    shutil.rmtree(destination, ignore_errors=True)
    destination.mkdir(parents=False, exist_ok=True)
    # Normalize repository, reference and output
    if not reference.endswith("/"):
        reference += "/"
    if not repository.endswith("/"):
        repository += "/"
    if output_directory.endswith("/"):
        output_directory = output_directory[:-1]
    # Build full repository URL
    repository_url = repository
    for additional_prefix in (reference, output_directory):
        repository_url = urljoin(repository_url, additional_prefix)
    # Generate all schemas
    for source in SOURCES.glob("*.json"):
        create_schema(
            source=source, output_directory=destination, ref_prefix=repository_url
        )


if __name__ == "__main__":
    main(
        repository=environ.get("REPOSITORY", REPOSITORY),
        reference=environ.get("REFERENCE", REFERENCE),
        output_directory=environ.get("OUTPUT", OUTPUT),
    )
