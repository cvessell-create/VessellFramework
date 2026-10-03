import hashlib
from pathlib import Path

import install_vesselframework_v3_8 as sync


def test_sync_replace_matches_source_and_records_read_back_hash(tmp_path, monkeypatch) -> None:
    source = tmp_path / "canonical.md"
    source.write_text("Canonical skill\n", encoding="utf-8")
    monkeypatch.setattr(sync, "TARGET_ROOT", tmp_path)
    cfg = {"source": source, "role": "live_skill", "mode": "replace", "required": True}
    result = sync.sync_one("/copy/SKILL.md", cfg, True, True, tmp_path / "log.jsonl")
    assert result["status"] == "UPDATED"
    assert result["post_hash"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert (tmp_path / "copy/SKILL.md").read_bytes() == source.read_bytes()


def test_corrupted_readback_is_not_reported_as_synchronized(tmp_path, monkeypatch) -> None:
    source = tmp_path / "canonical.md"
    source.write_text("Canonical skill\n", encoding="utf-8")
    monkeypatch.setattr(sync, "TARGET_ROOT", tmp_path)
    monkeypatch.setattr(sync, "atomic_write_text", lambda target, text: target.write_text("wrong"))
    cfg = {"source": source, "role": "live_skill", "mode": "replace", "required": True}
    result = sync.sync_one("/copy/SKILL.md", cfg, True, True, tmp_path / "log.jsonl")
    assert result["status"] == "ERROR"
    assert "Post-write hash" in result["error"]


def test_packaged_skill_copy_matches_canonical_bytes() -> None:
    assert Path("SKILL.md").read_bytes() == Path(
        "mnt/skills/user/vessel-framework-analyst/SKILL.md"
    ).read_bytes()
