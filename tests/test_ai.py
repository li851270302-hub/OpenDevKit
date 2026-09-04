from pathlib import Path

from opendevkit.ai import _repo_context


def test_selected_path_limits_source_context(tmp_path: Path):
    selected = tmp_path / "selected.py"
    ignored = tmp_path / "ignored.py"
    selected.write_text("SELECTED_ONLY = True\n", encoding="utf-8")
    ignored.write_text("IGNORED_ONLY = True\n", encoding="utf-8")

    context = _repo_context(tmp_path, selected_paths=[selected])

    assert "Selected source files: selected.py" in context
    assert "--- selected.py ---" in context
    assert "SELECTED_ONLY" in context
    assert "--- ignored.py ---" not in context
    assert "IGNORED_ONLY" not in context


def test_default_context_remains_repository_wide(tmp_path: Path):
    first = tmp_path / "first.py"
    second = tmp_path / "second.py"
    first.write_text("FIRST_FILE = True\n", encoding="utf-8")
    second.write_text("SECOND_FILE = True\n", encoding="utf-8")

    context = _repo_context(tmp_path)

    assert "--- first.py ---" in context
    assert "--- second.py ---" in context


def test_default_context_respects_project_exclusions(tmp_path: Path):
    included = tmp_path / "included.py"
    excluded_dir = tmp_path / "generated"
    excluded_dir.mkdir()
    excluded = excluded_dir / "excluded.py"
    included.write_text("INCLUDED = True\n", encoding="utf-8")
    excluded.write_text("EXCLUDED = True\n", encoding="utf-8")
    (tmp_path / ".opendevkit.toml").write_text(
        '[scan]\nexclude = ["generated/**"]\n',
        encoding="utf-8",
    )

    context = _repo_context(tmp_path)

    assert "Configured exclusions: generated/**" in context
    assert "INCLUDED = True" in context
    assert "EXCLUDED = True" not in context


def test_explicit_review_can_select_an_excluded_file(tmp_path: Path):
    excluded = tmp_path / "generated.py"
    excluded.write_text("EXPLICIT = True\n", encoding="utf-8")
    (tmp_path / ".opendevkit.toml").write_text(
        '[scan]\nexclude = ["generated.py"]\n',
        encoding="utf-8",
    )

    context = _repo_context(tmp_path, selected_paths=[excluded])

    assert "--- generated.py ---" in context
    assert "EXPLICIT = True" in context
