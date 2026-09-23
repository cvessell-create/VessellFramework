import importlib.util
from pathlib import Path

module_path = Path(__file__).parents[1] / "VesselFramework_SingleFile_EvilTwin_v0.2.py"
spec = importlib.util.spec_from_file_location("vessel_single_file_v02", module_path)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def test_evil_twin_skill_is_embedded() -> None:
    assert "VesselFramework_Evil_Twin_Adversarial_Analyst_SKILL_v0.1.md" in runtime.list_resources()


def test_offline_twin_flags_control_claims() -> None:
    findings = runtime.offline_twin(
        "The firewall always completely prevents lateral movement. "
        "The VPN makes internal users trusted. An IDS will block the attack."
    )

    assert "CLAIM BOUNDARY" in findings
    assert "PLACEMENT/MECHANISM" in findings
    assert "DEPENDENCY" in findings
