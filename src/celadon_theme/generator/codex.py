import json
import logging
import plistlib
from pathlib import Path

from jinja2 import Environment

from celadon_theme.config.paths import CODEX_DIR
from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.generator.vscode import VSCODE_THEME_TEMPLATE
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

logger = logging.getLogger(__name__)

# The rendered VS Code theme is the source of the token rules, since its
# tokenColors array carries the same scope and settings data as a TextMate
# theme in JSON form.
TM_THEME_TEMPLATE = "codex.tmTheme.j2"


class CodexGenerator(AbstractThemeGenerator):
    """
    Generator for the Codex CLI tmTheme.

    Codex renders syntax with syntect, so the theme is a standard TextMate
    plist. The token rules are derived from the rendered VS Code theme, which
    keeps the VS Code template as the single source of truth for token colors.
    The tmTheme structure, base background, and diff scopes live in the
    codex.tmTheme.j2 template.
    """

    def __init__(
        self,
        palette: PaletteModel,
        config: ConfigModel,
        env: Environment,
        dist_path: Path = CODEX_DIR,
    ) -> None:
        super().__init__(palette, config, env)
        self.dist_path = dist_path

    def generate_theme_files(self) -> None:
        """
        Generate the tmTheme plist from the rendered VS Code token rules.
        """
        logger.info("Generating %s theme files", self)
        self.dist_path.mkdir(parents=True, exist_ok=True)

        token_rules = self._render_token_rules()
        out_path = self.dist_path / "celadon.tmTheme"
        self._render_to_file(TM_THEME_TEMPLATE, out_path, token_rules=token_rules)

        self._validate_theme_file(out_path)

        logger.info("%s theme files generated", self)

    def generate_theme_metadata(self) -> None:
        """
        No-op. The tmTheme is installed manually and requires no packaging.
        """
        logger.info("%s has no metadata to generate, skipping", self)

    def _render_token_rules(self) -> list[dict[str, object]]:
        """
        Render the VS Code theme template and normalize its tokenColors.
        """
        context = {
            **self.palette.model_dump(),
            "theme": self.palette.theme,
            "config": self.config.model_dump(),
        }
        content = self.env.get_template(VSCODE_THEME_TEMPLATE).render(**context)
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            message = "Rendered VS Code theme is not valid JSON."
            raise ValueError(message) from exc
        if not isinstance(data, dict):
            message = "Rendered VS Code theme must be a JSON object."
            raise TypeError(message)
        if "tokenColors" not in data:
            message = "Rendered VS Code theme is missing the tokenColors array."
            raise ValueError(message)
        token_colors = data["tokenColors"]
        if not isinstance(token_colors, list):
            message = "Rendered VS Code theme tokenColors must be a list."
            raise TypeError(message)
        return [self._normalize_rule(rule) for rule in token_colors]

    def _normalize_rule(self, rule: object) -> dict[str, object]:
        """
        Normalize one VS Code token rule for the tmTheme template.
        """
        if not isinstance(rule, dict):
            message = "Rendered VS Code theme token rule must be a dictionary."
            raise TypeError(message)
        settings = rule.get("settings", {})
        if not isinstance(settings, dict):
            message = "Rendered VS Code theme token settings must be a dictionary."
            raise TypeError(message)
        scope = rule.get("scope", [])
        if isinstance(scope, list):
            scope_string = ", ".join(str(item) for item in scope)
        else:
            scope_string = str(scope)
        return {
            "name": rule.get("name", ""),
            # An empty scope would render as a match-all selector in
            # TextMate, so it maps to None and the template omits the key.
            "scope": scope_string or None,
            "font_style": settings.get("fontStyle"),
            "foreground": settings.get("foreground"),
        }

    def _validate_theme_file(self, out_path: Path) -> None:
        """
        Fail fast if the rendered tmTheme is not a parseable plist.
        """
        try:
            data = plistlib.loads(out_path.read_bytes())
        except plistlib.InvalidFileException as exc:
            message = f"Rendered theme file {out_path} is not a valid plist: {exc}"
            raise ValueError(message) from exc
        if not isinstance(data, dict):
            message = f"Rendered theme file {out_path} must be a plist dictionary."
            raise TypeError(message)
        settings = data.get("settings")
        if settings is None:
            message = f"Rendered theme file {out_path} is missing the settings array."
            raise ValueError(message)
        if not isinstance(settings, list):
            message = f"Rendered theme file {out_path} settings must be a list."
            raise TypeError(message)
