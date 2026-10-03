import json
from pathlib import Path


def test_distribution_manifest_has_only_unique_source_artifacts():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "VessellFramework_v3.8.1_SHA256_Manifest.json").read_text())
    paths = [entry["path"] for entry in manifest["files"]]
    assert len(paths) == len(set(paths))
    for name in paths:
        path = Path(name)
        assert not path.is_absolute()
        assert ".." not in path.parts
        assert all(not part.endswith(".egg-info") for part in path.parts)
        assert not set(path.parts) & {
            ".git", ".venv", "build", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
        }
        assert name != ".env"
        assert (root / path).is_file()
