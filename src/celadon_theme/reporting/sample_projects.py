import logging
import os
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from pathspec import PathSpec

from celadon_theme.config.paths import ROOT_DIR

logger = logging.getLogger(__name__)

# Directory names that never contribute source-file tokens.  They are pruned
# during traversal so vendored and generated content is not walked.
SKIPPED_DIRS = frozenset(
    {
        ".git",
        ".gradle",
        ".hg",
        ".idea",
        ".pytest_cache",
        ".ruff_cache",
        ".svn",
        ".tox",
        ".venv",
        ".vs",
        ".vscode",
        "__pycache__",
        "bower_components",
        "build",
        "cmake-build",
        "cmake-build-debug",
        "cmake-build-release",
        "dist",
        "node_modules",
        "out",
        "target",
        "venv",
        "vendor",
    }
)


@lru_cache
def _load_gitignore(directory: Path) -> PathSpec | None:
    gitignore = directory / ".gitignore"
    if gitignore.exists():
        lines = gitignore.read_text(encoding="utf-8").splitlines()
        return PathSpec.from_lines("gitignore", lines)
    return None


def get_sample_project_file_coverage(root: Path) -> dict[str, list[str]]:
    root_gitignore = _load_gitignore(root)
    result = defaultdict(set)

    for project_dir in sorted(
        p for p in root.iterdir() if p.is_dir() and p.name not in SKIPPED_DIRS
    ):
        project_gitignore = _load_gitignore(project_dir)
        for dirpath, dirnames, filenames in os.walk(project_dir):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIPPED_DIRS)
            for name in filenames:
                file_path = Path(dirpath) / name

                if root_gitignore and root_gitignore.match_file(
                    str(file_path.relative_to(root))
                ):
                    continue

                relative_to_project = file_path.relative_to(project_dir)
                if project_gitignore and project_gitignore.match_file(
                    str(relative_to_project)
                ):
                    continue

                # Skip the .gitignore file itself from coverage tokens.
                if name == ".gitignore":
                    continue

                # Determine the token to record:
                # If the file has a standard suffix, keep it (e.g., ".py").
                # Otherwise, use the full filename (e.g., "Dockerfile", ".env").
                token = file_path.suffix or file_path.name
                result[project_dir.name].add(token)

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
    stats_file = ROOT_DIR / "STATS.md"

    content = render_sample_coverage(coverage)
    section = (
        f"<!-- section:sample-coverage -->\n"
        f"{content}\n"
        f"<!-- /section:sample-coverage -->"
    )

    if not stats_file.exists():
        logger.info("%s not found, creating new file", stats_file.name)
        stats_file.write_text(
            f"# celadon-theme\n\n## Sample Project Coverage\n\n{section}\n",
            encoding="utf-8",
        )
        return

    logger.info("Updating sample coverage section in %s", stats_file.name)
    md = stats_file.read_text(encoding="utf-8")
    new_md, n_subs = re.subn(
        r"<!-- section:sample-coverage -->.*?<!-- /section:sample-coverage -->",
        section,
        md,
        flags=re.DOTALL,
    )
    if n_subs == 0:
        logger.warning(
            "%s missing coverage markers, appending section", stats_file.name
        )
        new_md = f"{md.rstrip()}\n\n## Sample Project Coverage\n\n{section}\n"
    stats_file.write_text(new_md, encoding="utf-8")
    logger.info("Successfully updated %s", stats_file.name)


def update_stats_report(sample_projects_dir: Path) -> None:
    logger.info(
        "Generating sample project coverage report from %s", sample_projects_dir
    )
    coverage = get_sample_project_file_coverage(sample_projects_dir)
    write_report(coverage)
