# References — works VessellFramework builds on

The framework operationalizes three published results, applied to the
problem of claim correction: claims enter, harden, get disavowed, and get
corrected, and the failure modes of that lifecycle are failures of
causal order. Each entry below is followed by what the framework takes
from it.

## Foundational works

**Lamport, L. (1978).** *Time, clocks, and the ordering of events in a
distributed system.* Communications of the ACM, 21(7), 558–565.
https://doi.org/10.1145/359545.359563

*What the framework takes from it:* the happens-before relation (*a → b*).
Every rule of the correction playbook is a rule about causal paths — which
events may follow which, and what must travel the path between them. Claim
versions and status timestamps reify a claim's causal history as data, the
same move as Lamport's logical clocks.

**Castello, J., Redmond, P., & Kuper, L. (2024).** *Inductive diagrams for
causal reasoning.* arXiv:2307.10484 [cs.PL]. Submitted July 19, 2023;
v2 May 14, 2024. https://arxiv.org/abs/2307.10484

*What the framework takes from it:* causal relationships are *witnessed by
the paths information follows* — happens-before modeled as paths between
events (mechanized in Agda). The framework's correction records carry
`causal_path` (the witnessed path from originating claim to correction),
dependents register *how* a claim reached them (`via`), and a negative
finding's search history is its witnessed path. This paper is the spine of
Section 4 of the case study.

**Redmond, P., Shen, G., Vazou, N., & Kuper, L. (2022).** *Verified causal
broadcast with Liquid Haskell.* arXiv:2206.14767 [cs.PL].
https://arxiv.org/abs/2206.14767

*What the framework takes from it:* the machine-checked guarantee that
messages are never delivered in an order violating causality. The
dependents registry (`register_dependent` / `deliver_correction` /
`confirm_dependent_update`, with `CausalOrderingError` on ordering
violations) is that guarantee in miniature: no dependent applies a
correction for a claim it never received, and no dependent is silently
marked corrected out of order.

## The framework's own paper

**Vessell, C. R. (2026).** *How an unverified sentence became system
behavior — and how to stop it.* Claim-correction case study, governing
spec for this codebase: [docs/claim-correction-case-study.md](claim-correction-case-study.md).

*What it is:* the worked incident (September 2026) from which the framework
was reconciled head-to-toe — provenance-tagged intake, consequential-use
gates, dependents registries, supersession-based correction,
re-validation — plus the September 30 rebuild of Section 4 around the three
works above, and the Section 6 meta-note recording the analyst's own
citation-verification miss as a second worked example.
