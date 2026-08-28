"""Exercise an installed wheel, not an editable source tree; no API calls."""

import json
from pathlib import Path
import subprocess
import sys
import sysconfig
import tempfile


def main() -> None:
    expected_version = sys.argv[1]
    scripts_dir = Path(sysconfig.get_path("scripts"))
    executable = scripts_dir / ("opendev.exe" if sys.platform == "win32" else "opendev")
    if not executable.is_file():
        raise AssertionError(f"Console entry point was not installed: {executable}")

    with tempfile.TemporaryDirectory(prefix="opendevkit-smoke-") as directory:
        root = Path(directory)

        def run(*arguments: str, status: int = 0) -> str:
            result = subprocess.run(
                [str(executable), *arguments],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if result.returncode != status:
                raise AssertionError(
                    f"{arguments}: expected exit {status}, got {result.returncode}\n"
                    f"{result.stdout}\n{result.stderr}"
                )
            return result.stdout

        assert run("version").strip() == expected_version
        assert "analyze" in run("--help")
        (root / "main.py").write_text("print('local trial')\n", encoding="utf-8")
        summary = json.loads(run("analyze", ".", "--json"))
        assert summary["files"] == 1
        assert "Python" in summary["languages"]
        for command in ("security", "deps", "prompt-scan"):
            assert json.loads(run(command, ".", "--json")) == []
        run("report", ".", "--output", "report.md")
        assert (root / "report.md").is_file()

        # A synthetic marker, not a real credential. The fixture is only scanned.
        marker = "x" * 20
        (root / "config.py").write_text(f'API_KEY = "{marker}"\n', encoding="utf-8")
        findings = json.loads(run("security", ".", "--json", "--fail-on", "high", status=1))
        assert any(item["rule"] == "possible-api-key" for item in findings)
        assert marker not in json.dumps(findings)

    print(f"Installed wheel {expected_version}: CLI smoke checks passed (no API calls).")


if __name__ == "__main__":
    main()
