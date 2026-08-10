from pathlib import Path
from typing import ClassVar

from celadon_theme.config.paths import CLAUDE_CODE_DIR
from celadon_theme.generator.single_file import SingleFileThemeGenerator


class ClaudeCodeGenerator(SingleFileThemeGenerator):
    """
    Generator for Claude Code themes.
    """

    template_name: ClassVar[str] = "claude-code-theme.json.j2"
    output_file_name: ClassVar[str] = "celadon-claude-code.json"
    dist_dir: ClassVar[Path] = CLAUDE_CODE_DIR
    label: ClassVar[str] = "Claude Code"
