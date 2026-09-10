import json
from pathlib import Path
from urllib.parse import quote

from . import __version__
from .models import Finding


SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
SARIF_VERSION = "2.1.0"
SARIF_LEVELS = {
    "high": "error",
    "medium": "warning",
    "low": "note",
}


def _artifact_uri(path: str) -> str:
    normalized = path.replace("\\", "/")
    return quote(normalized, safe="/:@-._~")


def build_sarif(findings: list[Finding]) -> dict:
    """Build a deterministic SARIF 2.1.0 document from scan findings."""
    rule_messages: dict[str, str] = {}
    rule_severities: dict[str, str] = {}
    for finding in findings:
        rule_messages.setdefault(finding.rule, finding.message)
        rule_severities.setdefault(finding.rule, finding.severity.lower())

    rule_ids = sorted(rule_messages)
    rule_indexes = {rule_id: index for index, rule_id in enumerate(rule_ids)}
    rules = [
        {
            "id": rule_id,
            "shortDescription": {"text": rule_messages[rule_id]},
            "defaultConfiguration": {
                "level": SARIF_LEVELS.get(rule_severities[rule_id], "warning")
            },
        }
        for rule_id in rule_ids
    ]

    results = []
    for finding in findings:
        physical_location = {
            "artifactLocation": {"uri": _artifact_uri(finding.path)}
        }
        if finding.line is not None:
            physical_location["region"] = {"startLine": finding.line}

        results.append({
            "ruleId": finding.rule,
            "ruleIndex": rule_indexes[finding.rule],
            "level": SARIF_LEVELS.get(finding.severity.lower(), "warning"),
            "message": {"text": finding.message},
            "locations": [{"physicalLocation": physical_location}],
        })

    return {
        "$schema": SARIF_SCHEMA,
        "version": SARIF_VERSION,
        "runs": [{
            "tool": {
                "driver": {
                    "name": "OpenDevKit",
                    "informationUri": "https://github.com/li851270302-hub/OpenDevKit",
                    "semanticVersion": __version__,
                    "rules": rules,
                }
            },
            "results": results,
        }],
    }


def write_sarif(path: Path, findings: list[Finding]) -> None:
    path.write_text(
        json.dumps(build_sarif(findings), indent=2) + "\n",
        encoding="utf-8",
    )
