from pathlib import Path
from typing import ClassVar

from celadon_theme.config.paths import QWEN_CODE_DIR
from celadon_theme.generator.single_file import SingleFileThemeGenerator


class QwenCodeGenerator(SingleFileThemeGenerator):
    """
    Generator for Qwen Code custom themes.
    """

    template_name: ClassVar[str] = "qwen-code-theme.json.j2"
    output_file_name: ClassVar[str] = "celadon-qwen-code.json"
    dist_dir: ClassVar[Path] = QWEN_CODE_DIR
