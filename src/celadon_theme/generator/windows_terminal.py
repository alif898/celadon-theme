from pathlib import Path
from typing import ClassVar

from celadon_theme.config.paths import WINDOWS_TERMINAL_DIR
from celadon_theme.generator.single_file import SingleFileThemeGenerator


class WindowsTerminalGenerator(SingleFileThemeGenerator):
    """
    Generator for Windows Terminal themes.
    """

    template_name: ClassVar[str] = "windows-terminal-theme.json.j2"
    output_file_name: ClassVar[str] = "celadon-windows-terminal.json"
    dist_dir: ClassVar[Path] = WINDOWS_TERMINAL_DIR
    label: ClassVar[str] = "Windows Terminal"
