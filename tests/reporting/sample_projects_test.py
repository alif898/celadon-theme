from pathlib import Path
from unittest.mock import patch

import pytest

from celadon_theme.reporting.sample_projects import (
    get_sample_project_file_coverage,
    render_sample_coverage,
    update_stats_report,
    write_report,
)


@pytest.fixture
def sample_projects_dir(tmp_path: Path) -> Path:
    (tmp_path / "python" / "src").mkdir(parents=True)
    (tmp_path / "python" / "src" / "main.py").touch()
    (tmp_path / "python" / "src" / "utils.py").touch()
    (tmp_path / "python" / "pyproject.toml").touch()

    (tmp_path / "java" / "src").mkdir(parents=True)
    (tmp_path / "java" / "src" / "Main.java").touch()
    (tmp_path / "java" / "pom.xml").touch()

    (tmp_path / "typescript" / "src").mkdir(parents=True)
    (tmp_path / "typescript" / "src" / "index.ts").touch()
    (tmp_path / "typescript" / "src" / "App.tsx").touch()
    (tmp_path / "typescript" / "package.json").touch()

    return tmp_path


@pytest.fixture
def existing_stats_file(tmp_path: Path) -> Path:
    stats_file = tmp_path / "STATS.md"
    stats_file.write_text(
        "# Celadon Theme — Stats\n\n"
        "## Sample Project Coverage\n\n"
        "<!-- section:sample-coverage -->\n"
        "old content\n"
        "<!-- /section:sample-coverage -->\n",
        encoding="utf-8",
    )
    return stats_file


def test_returns_extensions_per_project(sample_projects_dir: Path) -> None:
    result = get_sample_project_file_coverage(sample_projects_dir)
    assert result["python"] == [".py", ".toml"]
    assert result["java"] == [".java", ".xml"]
    assert result["typescript"] == [".json", ".ts", ".tsx"]


def test_extensions_are_sorted(sample_projects_dir: Path) -> None:
    result = get_sample_project_file_coverage(sample_projects_dir)
    for extensions in result.values():
        assert extensions == sorted(extensions)


def test_ignores_empty_project_folders(tmp_path: Path) -> None:
    (tmp_path / "empty").mkdir()
    result = get_sample_project_file_coverage(tmp_path)
    assert "empty" not in result


def test_ignores_root_level_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").touch()
    (tmp_path / "python").mkdir()
    (tmp_path / "python" / "main.py").touch()
    result = get_sample_project_file_coverage(tmp_path)
    assert ".md" not in result.get("python", [])


def test_empty_directory_returns_empty_dict(tmp_path: Path) -> None:
    result = get_sample_project_file_coverage(tmp_path)
    assert result == {}


def test_ignores_files_without_extension(tmp_path: Path) -> None:
    (tmp_path / "python").mkdir()
    (tmp_path / "python" / "Makefile").touch()
    (tmp_path / "python" / "main.py").touch()
    result = get_sample_project_file_coverage(tmp_path)
    assert "" not in result["python"]


def test_gitignore_is_respected(tmp_path: Path) -> None:
    (tmp_path / "python").mkdir()
    (tmp_path / "python" / "main.py").touch()
    (tmp_path / "python" / "ignored.pyc").touch()
    (tmp_path / "python" / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
    result = get_sample_project_file_coverage(tmp_path)
    assert ".pyc" not in result["python"]


def test_root_gitignore_is_respected(tmp_path: Path) -> None:
    (tmp_path / "python").mkdir()
    (tmp_path / "python" / "main.py").touch()
    (tmp_path / "python" / "dist" / "output.js").mkdir(parents=True) if False else None
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "output.js").touch()
    (tmp_path / ".gitignore").write_text("dist/\n", encoding="utf-8")
    result = get_sample_project_file_coverage(tmp_path)
    assert ".js" not in result.get("dist", [])


def test_render_contains_table_headers() -> None:
    result = render_sample_coverage({"python": [".py"]})
    assert "| Project | Extensions |" in result
    assert "|---|---|" in result


def test_render_contains_project_rows() -> None:
    result = render_sample_coverage({"python": [".py", ".toml"], "java": [".java"]})
    assert "| python | .py, .toml |" in result
    assert "| java | .java |" in result


def test_render_projects_are_sorted() -> None:
    result = render_sample_coverage(
        {"typescript": [".ts"], "java": [".java"], "python": [".py"]}
    )
    assert result.index("java") < result.index("python") < result.index("typescript")


def test_render_empty_coverage() -> None:
    result = render_sample_coverage({})
    assert "| Project | Extensions |" in result
    assert "|---|---|" in result


def test_creates_new_stats_file_if_not_exists(tmp_path: Path) -> None:
    stats_file = tmp_path / "STATS.md"
    with patch("celadon_theme.reporting.sample_projects.Path") as mock_path:
        mock_path.return_value = stats_file
        write_report({"python": [".py"]})
    assert stats_file.exists()
    assert "Sample Project Coverage" in stats_file.read_text(encoding="utf-8")


def test_updates_existing_section(existing_stats_file: Path) -> None:
    with patch("celadon_theme.reporting.sample_projects.Path") as mock_path:
        mock_path.return_value = existing_stats_file
        write_report({"python": [".py"]})
    content = existing_stats_file.read_text(encoding="utf-8")
    assert "old content" not in content
    assert "python" in content


def test_preserves_content_outside_section(existing_stats_file: Path) -> None:
    existing_stats_file.write_text(
        "# Celadon Theme — Stats\n\n"
        "Some other content\n\n"
        "<!-- section:sample-coverage -->\n"
        "old content\n"
        "<!-- /section:sample-coverage -->\n",
        encoding="utf-8",
    )
    with patch("celadon_theme.reporting.sample_projects.Path") as mock_path:
        mock_path.return_value = existing_stats_file
        write_report({"python": [".py"]})
    assert "Some other content" in existing_stats_file.read_text(encoding="utf-8")


def test_update_stats_report_writes_all_projects(
    sample_projects_dir: Path, tmp_path: Path
) -> None:
    stats_file = tmp_path / "STATS.md"
    with patch("celadon_theme.reporting.sample_projects.Path") as mock_path:
        mock_path.return_value = stats_file
        update_stats_report(sample_projects_dir)
    content = stats_file.read_text(encoding="utf-8")
    assert "python" in content
    assert "java" in content
    assert "typescript" in content
