from pathlib import Path
from typing import ClassVar

from celadon_theme.config.paths import OPENCODE_DIR
from celadon_theme.generator.single_file import SingleFileThemeGenerator


class OpenCodeGenerator(SingleFileThemeGenerator):
    """
    Generator for OpenCode themes.

    OpenCode derives the theme name from the file name rather than a
    "name" key inside the JSON, and its schema forbids extra top-level
    properties, so the name check is disabled for this target. The
    rendered theme is validated for well-formed JSON and hex colors only.
    """

    template_name: ClassVar[str] = "opencode-theme.json.j2"
    output_file_name: ClassVar[str] = "celadon-opencode.json"
    dist_dir: ClassVar[Path] = OPENCODE_DIR
    label: ClassVar[str] = "OpenCode"
    validate_name: ClassVar[bool] = False
