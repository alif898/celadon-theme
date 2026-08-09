import json
import re
from pathlib import Path
from typing import ClassVar

from celadon_theme.config.paths import PI_DIR
from celadon_theme.generator.single_file import SingleFileThemeGenerator

_HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
_MAX_PALETTE_INDEX = 255


class PiGenerator(SingleFileThemeGenerator):
    """
    Generator for Pi themes.

    Pi only supports 6-digit hex colors (#RRGGBB). Its runtime parser
    (hexToRgb in pi's theme.ts) throws on any hex string that is not
    exactly 6 characters. The 8-digit RGBA palette entries (the chromatic
    *_alt2 keys such as green_alt2 or red_alt2) must therefore never be
    used in the Pi template. Use 6-digit keys instead, or add new
    precomposited 6-digit palette entries when a tinted background is
    wanted. Generation validates the rendered colors against this
    contract and fails fast if it is violated.
    """

    template_name: ClassVar[str] = "pi-theme.json.j2"
    output_file_name: ClassVar[str] = "celadon-pi.json"
    dist_dir: ClassVar[Path] = PI_DIR

    def generate_theme_files(self) -> None:
        """
        Generate the theme JSON file, then validate its color values.
        """
        super().generate_theme_files()
        self.validate_theme_colors(self.dist_path / self.output_file_name)

    def validate_theme_colors(self, theme_file: Path) -> None:
        """
        Fail fast if a rendered color is not supported by Pi.

        Pi accepts an empty string (terminal default), a 256-color
        palette index, or 6-digit hex (#RRGGBB). Anything else, such as
        an 8-digit RGBA hex value, would throw in Pi's runtime parser, so
        it is treated as a generation error.
        """
        data = json.loads(theme_file.read_text(encoding="utf-8"))
        for token, value in data.get("colors", {}).items():
            # bool is a subclass of int, so JSON true/false must be excluded
            # from the palette-index branch explicitly. Pi does not support
            # boolean colors.
            if isinstance(value, int) and not isinstance(value, bool):
                if 0 <= value <= _MAX_PALETTE_INDEX:
                    continue
                msg = (
                    f"Invalid Pi color index {value} for token {token!r}: "
                    "expected 0-255"
                )
                raise ValueError(msg)
            if isinstance(value, str) and (
                value == "" or _HEX_COLOR_PATTERN.match(value)
            ):
                continue
            msg = (
                f"Invalid Pi color {value!r} for token {token!r}: Pi only "
                "supports 6-digit hex (#RRGGBB), an empty string, or a "
                "256-color palette index"
            )
            raise ValueError(msg)
