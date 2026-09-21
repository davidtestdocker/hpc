"""Bootstrap 下載來源必須通過釘版 checksum 才能使用。"""

import hashlib
from io import BytesIO

import pytest

from scripts import bootstrap_cluster


class Download(BytesIO):
    """讓 BytesIO 支援 urllib response 使用的 context manager。"""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def test_controller_manifest_checksum_is_verified(monkeypatch, tmp_path):
    content = b"apiVersion: v1\nkind: List\n"
    monkeypatch.setitem(bootstrap_cluster.CONTROLLERS, "test", {
        "url": "https://example.invalid/manifest.yaml",
        "sha256": hashlib.sha256(content).hexdigest(),
    })
    monkeypatch.setattr(bootstrap_cluster.urllib.request, "urlopen",
                        lambda *args, **kwargs: Download(content))
    target = tmp_path / "manifest.yaml"
    bootstrap_cluster.download_controller("test", target)
    assert target.read_bytes() == content


def test_controller_manifest_checksum_mismatch_is_rejected(monkeypatch, tmp_path):
    monkeypatch.setitem(bootstrap_cluster.CONTROLLERS, "test", {
        "url": "https://example.invalid/manifest.yaml",
        "sha256": "0" * 64,
    })
    monkeypatch.setattr(bootstrap_cluster.urllib.request, "urlopen",
                        lambda *args, **kwargs: Download(b"changed"))
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        bootstrap_cluster.download_controller("test", tmp_path / "manifest.yaml")


def test_postgres_env_requires_nonempty_credentials(tmp_path):
    valid = tmp_path / "valid.env"
    valid.write_text("POSTGRES_USER=platform\nPOSTGRES_PASSWORD=secret\n")
    assert bootstrap_cluster.validate_postgres_env(valid) == {
        "POSTGRES_USER", "POSTGRES_PASSWORD"
    }

    invalid = tmp_path / "invalid.env"
    invalid.write_text("POSTGRES_USER=platform\nPOSTGRES_PASSWORD=\n")
    with pytest.raises(RuntimeError, match="必要且非空"):
        bootstrap_cluster.validate_postgres_env(invalid)

    placeholder = tmp_path / "placeholder.env"
    placeholder.write_text("POSTGRES_USER=platform\nPOSTGRES_PASSWORD=CHANGE_ME\n")
    with pytest.raises(RuntimeError, match="CHANGE_ME"):
        bootstrap_cluster.validate_postgres_env(placeholder)
