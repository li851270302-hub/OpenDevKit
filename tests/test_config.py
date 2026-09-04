from pathlib import Path

import pytest

from opendevkit.config import ConfigurationError, load_config


def test_rejects_malformed_toml(tmp_path: Path):
    (tmp_path / ".opendevkit.toml").write_text("[scan\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Could not parse"):
        load_config(tmp_path)


def test_rejects_parent_relative_exclusion(tmp_path: Path):
    (tmp_path / ".opendevkit.toml").write_text(
        '[scan]\nexclude = ["../shared/**"]\n',
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="must stay relative"):
        load_config(tmp_path)


def test_rejects_windows_absolute_exclusion(tmp_path: Path):
    (tmp_path / ".opendevkit.toml").write_text(
        '[scan]\nexclude = ["C:\\\\private\\\\**"]\n',
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="must stay relative"):
        load_config(tmp_path)


def test_rejects_symlinked_configuration(tmp_path: Path):
    target = tmp_path / "settings.toml"
    target.write_text('[scan]\nexclude = []\n', encoding="utf-8")
    config = tmp_path / ".opendevkit.toml"
    try:
        config.symlink_to(target)
    except (NotImplementedError, OSError):
        pytest.skip("Symbolic links are not available on this platform")

    with pytest.raises(ConfigurationError, match="must not be a symbolic link"):
        load_config(tmp_path)
