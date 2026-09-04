from pathlib import Path

from opendevkit.report import build_report


def test_report_includes_security_and_dependency_findings(tmp_path: Path):
    secret = 'API_KEY = "' + ("x" * 20) + '"\n'
    (tmp_path / "config.py").write_text(secret, encoding="utf-8")
    (tmp_path / "requirements.txt").write_text(
        "requests>=2.0\nrich==13.7.0\n",
        encoding="utf-8",
    )

    report = build_report(tmp_path)

    assert "## Security findings" in report
    assert "possible-api-key" in report
    assert "## Dependency findings" in report
    assert "unpinned-dependency" in report


def test_report_discloses_and_respects_project_exclusions(tmp_path: Path):
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "secret.py").write_text(
        'API_KEY = "' + ("x" * 20) + '"\n',
        encoding="utf-8",
    )
    (tmp_path / ".opendevkit.toml").write_text(
        '[scan]\nexclude = ["generated/**"]\n',
        encoding="utf-8",
    )

    report = build_report(tmp_path)

    assert "Config excludes: `generated/**`" in report
    assert "possible-api-key" not in report
