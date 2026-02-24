import logging
import yaml
from jinja2 import Environment, FileSystemLoader, Template
from logging.config import dictConfig
from pathlib import Path
from typing import Any

from .config.logging_config import logging_config

dictConfig(logging_config.model_dump())
logger = logging.getLogger(__name__)


def load_config(path: Path) -> dict[str, Any]:
    with open(path, "r") as f:
        raw_data = yaml.safe_load(f)

    # Resolve internal YAML references
    logger.info("Resolving internal YAML references")
    yaml_as_str = yaml.dump(raw_data)
    resolved_str = Template(yaml_as_str).render(**raw_data)
    return yaml.safe_load(resolved_str)


def generate() -> None:
    root = Path(__file__).resolve().parent.parent.parent
    config = load_config(root / "templates/palette.yaml")

    env = Environment(loader=FileSystemLoader(str(root / "templates")))
    dist_path = root / "jetbrains/src/main/resources/themes"
    dist_path.mkdir(parents=True, exist_ok=True)

    # Render the templates
    files = {
        "celadon.icls.j2": "Celadon.xml",
        "celadon.theme.json.j2": "celadon.theme.json"
    }

    for tpl, out in files.items():
        content = env.get_template(tpl).render(**config)
        with open(dist_path / out, "w") as f:
            f.write(content)
    logger.info(f"Templates rendered successfully to {dist_path}")


def main() -> None:
    generate()


if __name__ == "__main__":
    main()