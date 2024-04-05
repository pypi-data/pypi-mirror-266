"""Generate the code reference pages."""

from pathlib import Path

import mkdocs_gen_files.nav


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
