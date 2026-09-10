import json
from pathlib import Path

from typer.testing import CliRunner

from opendevkit import __version__
from opendevkit.cli import app
from opendevkit.models import Finding
from opendevkit.sarif import SARIF_SCHEMA, build_sarif


runner = CliRunner()


def test_build_sarif_maps_rules_severity_paths_and_lines():
    findings = [
        Finding("secret", "high", "src/my key.py", 7, "Possible secret."),
        Finding("dependency", "low", "pyproject.toml", None, "Review version."),
        Finding("execution", "medium", "src/run.py", 2, "Review execution."),
    ]

    payload = build_sarif(findings)
    run = payload["runs"][0]

    assert payload["$schema"] == SARIF_SCHEMA
    assert payload["version"] == "2.1.0"
    assert run["tool"]["driver"]["semanticVersion"] == __version__
    assert [rule["id"] for rule in run["tool"]["driver"]["rules"]] == [
        "dependency",
        "execution",
        "secret",
    ]
    assert [result["level"] for result in run["results"]] == [
        "error",
        "note",
        "warning",
    ]
    first_location = run["results"][0]["locations"][0]["physicalLocation"]
    assert first_location["artifactLocation"]["uri"] == "src/my%20key.py"
    assert first_location["region"] == {"startLine": 7}
    second_location = run["results"][1]["locations"][0]["physicalLocation"]
    assert "region" not in second_location


def test_empty_findings_produce_valid_sarif():
    payload = build_sarif([])
    driver = payload["runs"][0]["tool"]["driver"]

    assert driver["rules"] == []
    assert payload["runs"][0]["results"] == []


def test_cli_writes_sarif_before_fail_on_exit(tmp_path: Path):
    source = 'API_KEY = "' + ("x" * 20) + '"\n'
    (tmp_path / "config.py").write_text(source, encoding="utf-8")
    output = tmp_path / "results.sarif"

    result = runner.invoke(
        app,
        [
            "security",
            str(tmp_path),
            "--sarif",
            str(output),
            "--fail-on",
            "high",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["runs"][0]["results"][0]["ruleId"] == "possible-api-key"


def test_prompt_scan_writes_empty_sarif(tmp_path: Path):
    output = tmp_path / "prompt.sarif"

    result = runner.invoke(
        app,
        ["prompt-scan", str(tmp_path), "--sarif", str(output)],
    )

    assert result.exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["runs"][0]["results"] == []
