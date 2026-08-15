import json
import logging
import re
from pathlib import Path
from typing import ClassVar

from jinja2 import Environment

from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

# Rendered colors must be hex strings in either the 6-digit RRGGBB form
# or the 8-digit RRGGBBAA form. Targets with stricter color contracts,
# such as Pi, override validation.
_HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")


class SingleFileThemeGenerator(AbstractThemeGenerator):
    """
    Base class for targets that ship a single generated theme JSON file.
    """

    template_name: ClassVar[str]
    output_file_name: ClassVar[str]
    dist_dir: ClassVar[Path]
    label: ClassVar[str]
    # Whether the rendered theme must carry a top-level "name" key matching
    # config.name. Targets whose format derives the theme name from the file
    # name (such as OpenCode) disable this check.
    validate_name: ClassVar[bool] = True

    def __init__(
        self,
        palette: PaletteModel,
        config: ConfigModel,
        env: Environment,
        dist_path: Path | None = None,
    ) -> None:
        super().__init__(palette, config, env)
        self.dist_path = dist_path or self.dist_dir

    @property
    def logger(self) -> logging.Logger:
        """
        Logger named after the concrete generator's module.
        """
        return logging.getLogger(self.__class__.__module__)

    def generate_theme_files(self) -> None:
        """
        Generate the theme JSON file into the dist directory, then validate it.
        """
        self.logger.info("Generating %s theme files", self)
        self.dist_path.mkdir(parents=True, exist_ok=True)

        out_path = self.dist_path / self.output_file_name
        self._render_to_file(self.template_name, out_path)
        self._validate_theme_file(out_path)

        self.logger.info("%s theme files generated", self)

    def generate_theme_metadata(self) -> None:
        """
        No-op. Single-file themes are installed manually and require no packaging.
        """
        self.logger.info("%s has no metadata to generate, skipping", self)

    def _validate_theme_file(self, out_path: Path) -> None:
        """
        Fail fast if the rendered theme is malformed JSON, has the wrong
        name, or contains an invalid hex color.
        """
        try:
            data = json.loads(out_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            message = f"Rendered theme file {out_path} is not valid JSON: {exc}"
            raise ValueError(message) from exc

        # A scalar or array is never a usable theme, so reject it before
        # any target-specific checks run.
        if not isinstance(data, dict):
            message = (
                f"Rendered theme file {out_path} must be a JSON object, "
                f"got {type(data).__name__}."
            )
            raise TypeError(message)

        if self.validate_name and data.get("name") != self.config.name:
            message = (
                f"Rendered theme file {out_path} has name {data.get('name')!r}, "
                f"expected {self.config.name!r}"
            )
            raise ValueError(message)

        self._validate_color_values(data, out_path)

    def _validate_color_values(self, value: object, out_path: Path) -> None:
        """
        Validate that every string starting with '#' in the theme is a hex color.
        """
        if isinstance(value, dict):
            for item in value.values():
                self._validate_color_values(item, out_path)
        elif isinstance(value, list):
            for item in value:
                self._validate_color_values(item, out_path)
        elif (
            isinstance(value, str)
            and value.startswith("#")
            and not _HEX_COLOR_PATTERN.match(value)
        ):
            message = (
                f"Invalid hex color {value!r} in theme file {out_path}: "
                "expected #RRGGBB or #RRGGBBAA"
            )
            raise ValueError(message)
