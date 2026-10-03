import json
from pathlib import Path

from vessell.game_architecture import ORIGINAL_COMMIT, ORIGINAL_SHA256


def test_game_component_map_covers_each_original_named_function_once():
    root = Path(__file__).resolve().parents[1]
    mapping = json.loads((root / "docs/game-component-map.json").read_text())
    assert mapping["original_commit"] == ORIGINAL_COMMIT
    assert mapping["original_index_sha256"] == ORIGINAL_SHA256
    names = [name for component in mapping["components"] for name in component["functions"]]
    assert len(names) == len(set(names)) == 35
    assert set(names) == {
        "setMessage", "tone", "title", "briefing", "parseMap", "loadLevel", "spawnEnemy",
        "solid", "moveEntity", "hasLOS", "use", "finishLevel", "victory", "die", "fire",
        "killEnemy", "damage", "cycleWeapon", "update", "enemyShoot", "wallColor", "render",
        "spriteScreen", "renderSprites", "drawEnemy", "drawPickup", "drawWeapon", "drawHUD",
        "drawMap", "loop", "initAudio", "pause", "joyMove", "joyEnd", "bindHold",
    }
    for component in mapping["components"]:
        assert (root / component["target"]).is_file()
    skill = (root / "GAME_DEVELOPMENT_SKILL.md").read_text()
    assert all(f"`{name}`" in skill for name in names)
    assert "Signal Recall" in skill
    assert "authoring" in mapping["evidence_level"]
