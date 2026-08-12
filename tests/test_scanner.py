from pathlib import Path

from opendevkit.scanner import analyze_repo, scan_security


def test_analyze_repo(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")

    summary = analyze_repo(tmp_path)

    assert summary.files == 2
    assert "Python" in summary.languages
    assert "main.py" in summary.entry_points


def test_detects_hardcoded_secret(tmp_path: Path):
    source = 'API_KEY = "' + ("x" * 20) + '"\n'
    (tmp_path / "config.py").write_text(source, encoding="utf-8")

    findings = scan_security(tmp_path)

    assert any(f.rule == "possible-api-key" for f in findings)


def test_detects_shell_true(tmp_path: Path):
    source = "import subprocess\nsubprocess.run(cmd, shell=True)\n"
    (tmp_path / "run.py").write_text(source, encoding="utf-8")

    findings = scan_security(tmp_path)

    assert any(f.rule == "shell-true" for f in findings)
