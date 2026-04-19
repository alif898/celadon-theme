import logging
import re
from collections import defaultdict
from pathlib import Path

import pathspec
from pathspec import PathSpec

logger = logging.getLogger(__name__)


def _load_gitignore(directory: Path) -> PathSpec | None:
    gitignore = directory / ".gitignore"
    if gitignore.exists():
        lines = gitignore.read_text(encoding="utf-8").splitlines()
        return pathspec.PathSpec.from_lines("gitignore", lines)
    return None


def get_sample_project_file_coverage(root: Path) -> dict[str, list[str]]:
    root_gitignore = _load_gitignore(root)
    result = defaultdict(set)

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(root)

        if len(relative_path.parts) <= 1:
            continue

        if root_gitignore and root_gitignore.match_file(str(relative_path)):
            continue

        first_subfolder = relative_path.parts[0]
        project_dir = root / first_subfolder

        project_gitignore = _load_gitignore(project_dir)
        relative_to_project = file_path.relative_to(project_dir)
        if project_gitignore and project_gitignore.match_file(str(relative_to_project)):
            continue

        # Skip the .gitignore file itself from coverage tokens
        if file_path.name == ".gitignore":
            continue

        # Determine the token to record:
        # If the file has a standard suffix, keep it (e.g., ".py").
        # If there is no suffix, use the full filename (e.g., "Dockerfile", ".env")
        token = file_path.suffix or file_path.name
        result[first_subfolder].add(token)

    final_result = {
        project: sorted(extensions) for project, extensions in result.items()
    }
    logger.info("Found %d sample projects: %s", len(result), final_result)
    return final_result


def render_sample_coverage(coverage: dict[str, list[str]]) -> str:
    logger.info("Rendering sample project coverage report")
    lines = []
    for project, extensions in sorted(coverage.items()):
        ext_str = ", ".join(extensions)
        lines.append(f"| {project} | {ext_str} |")

    return "\n".join(
        [
            "| Project | Extensions |",
            "|---|---|",
            *lines,
        ]
    )


def write_report(coverage: dict[str, list[str]]) -> None:
    stats_file = Path("STATS.md")

    content = render_sample_coverage(coverage)
    section = (
        f"<!-- section:sample-coverage -->\n"
        f"{content}\n"
        f"<!-- /section:sample-coverage -->"
    )

    if not stats_file.exists():
        logger.info("STATS.md not found, creating new file")
        stats_file.write_text(
            f"# celadon-theme\n\n## Sample Project Coverage\n\n{section}\n",
            encoding="utf-8",
        )
        return

    logger.info("Updating sample coverage section in STATS.md")
    md = stats_file.read_text(encoding="utf-8")
    md = re.sub(
        r"<!-- section:sample-coverage -->.*?<!-- /section:sample-coverage -->",
        section,
        md,
        flags=re.DOTALL,
    )
    stats_file.write_text(md, encoding="utf-8")
    logger.info("Successfully updated STATS.md")


def update_stats_report(sample_projects_dir: Path) -> None:
    logger.info(
        "Generating sample project coverage report from %s", sample_projects_dir
    )
    coverage = get_sample_project_file_coverage(sample_projects_dir)
    write_report(coverage)
