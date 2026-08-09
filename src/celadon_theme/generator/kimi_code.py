from pathlib import Path
from typing import ClassVar

from celadon_theme.config.paths import KIMI_CODE_DIR
from celadon_theme.generator.single_file import SingleFileThemeGenerator


class KimiCodeGenerator(SingleFileThemeGenerator):
    """
    Generator for Kimi Code custom themes.
    """

    template_name: ClassVar[str] = "kimi-code-theme.json.j2"
    output_file_name: ClassVar[str] = "celadon-kimi-code.json"
    dist_dir: ClassVar[Path] = KIMI_CODE_DIR
