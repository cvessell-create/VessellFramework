from vessell.provenance import EvidenceItem, ProvenanceRegistry, ProvenanceState, SourceStatus


def test_provenance_resolves_to_root() -> None:
    registry = ProvenanceRegistry()
    registry.register(EvidenceItem("root", SourceStatus.SOURCE_ESTABLISHED, "root"))
    registry.register(EvidenceItem("child", SourceStatus.SOURCE_ESTABLISHED, "child", "root"))

    result = registry.resolve("child")

    assert result.state == ProvenanceState.RESOLVED
    assert result.root_id == "root"


def test_missing_parent_is_not_independence() -> None:
    registry = ProvenanceRegistry()
    registry.register(EvidenceItem("orphan", SourceStatus.SOURCE_ESTABLISHED, "orphan", "missing"))

    result = registry.resolve("orphan")

    assert result.state == ProvenanceState.UNRESOLVED_PARENT
    assert registry.compare_independence(["orphan"])["independent"] is None
