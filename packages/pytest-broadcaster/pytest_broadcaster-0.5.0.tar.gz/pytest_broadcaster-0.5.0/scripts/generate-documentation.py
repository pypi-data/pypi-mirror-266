"""Generate the code reference pages."""

from __future__ import annotations

import json
import shutil
from os import environ
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import mkdocs_gen_files.nav

REPOSITORY = "https://charbonnierg.github.com/pytest-broadcaster"

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


def generate_schemas(ref_prefix: str, output_directory: str):
    # Validate reference and output
    if not (ref_prefix and output_directory):
        raise ValueError("repository and output_directory are required")
    if output_directory.startswith("/"):
        raise ValueError("output must be relative")
    # Clean output directory
    destination = Path(output_directory)
    shutil.rmtree(destination, ignore_errors=True)
    destination.mkdir(parents=False, exist_ok=True)
    # Normalize repository and output
    if not ref_prefix.endswith("/"):
        ref_prefix += "/"
    if output_directory.endswith("/"):
        output_directory = output_directory[:-1]
    # Build full repository URL
    target = output_directory
    if target.startswith("docs"):
        target = target[5:]
    ref_prefix = urljoin(ref_prefix, target)
    # Generate all schemas
    for source in SOURCES.glob("*.json"):
        create_schema(
            source=source, output_directory=destination, ref_prefix=ref_prefix
        )


def generate_license_file() -> None:
    """Generate the LICENSE.md file."""

    with mkdocs_gen_files.open("LICENSE.md", "w") as license_file:
        license = Path("LICENSE")
        if license.is_file():
            content = license.read_text()
            content += "\n\n"
            content += """
<style>
  .md-content__button {
    display: none;
  }
</style>
"""
            license_file.write(content)
        else:
            license_file.write("No license file found")


# generate_references()
generate_license_file()
generate_schemas(
    ref_prefix=environ.get("REPOSITORY", REPOSITORY),
    output_directory="docs/schemas",
)
