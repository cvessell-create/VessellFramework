# Free courses for applying evaluation methods

These are learning resources, not datasets or efficacy evidence. Use official
syllabi, exercises and publisher/instructor video channels. A free-to-watch
lecture is not automatically licensed for redistribution; this rebuild links
to the resources rather than copying videos, transcripts or course content.
No paid enrollment or account connection was performed.

| Framework application | Free course / official entry point | Method to practice | Deliverable that demonstrates application |
|---|---|---|---|
| Forecast uncertainty and score interpretation | [MIT OCW 18.05 Probability and Statistics](https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/) | Conditional probability, estimation, hypothesis tests and confidence intervals | Explicit forecast target, uncertainty, baseline and correctly aligned held-out outcome; do not interpret ordinal Llama weights as probabilities |
| Python behavior and output synchronization | [Harvard CS50 Python: Unit Tests](https://cs50.harvard.edu/python/weeks/5/) | Assertions, pytest, test organization and failure diagnosis | Positive/negative tests for actual serialized outputs, missing inputs and corrupt writes; unit tests do not establish external validity |
| Llama evaluation / classification methods | [Stanford CS229](https://cs229.stanford.edu/) | Generalization, bias/variance and model evaluation | Source/time-grouped train/validation/test split, frozen rubric and held-out labels; do not tune on the final evaluation set |
| Evidence-based reasoning and decision models | [UC Berkeley CS188 open course](https://inst.eecs.berkeley.edu/~cs188/archive/fa24/) and [maintained textbook](https://inst.eecs.berkeley.edu/~cs188/textbook/) | Logical/probabilistic reasoning, decision making and learning | State the assumptions of a decision model and test it against independently labeled cases; probability models do not establish source independence automatically |
| Claims of control efficacy | [Brady Neal's open causal-inference course](https://www.bradyneal.com/causal-inference-course) | Confounding, causal identification and comparison design | A written estimand, comparison group, causal assumptions and measured outcomes; an award or observational association is not causal proof |
| Defensive system/control design | [MIT OCW 6.858 Computer Systems Security](https://ocw.mit.edu/courses/6-858-computer-systems-security-fall-2014/) | Threat models, secure-system design and evaluating assumptions | Authorized defensive test plan, defined control objective and verified failure/rollback outcomes; no unsolicited scans or attacks |
| Foundational statistics refresher | [Khan Academy Statistics and Probability](https://www.khanacademy.org/math/statistics-probability) | Probability, sampling, inference and interpreting study results | Worked calculations cross-checked against an independent implementation. The dynamically loaded course page could not be inspected fully in this review |
| Official lecture videos on YouTube | [MIT OpenCourseWare](https://www.youtube.com/@mitocw), [CS50](https://www.youtube.com/cs50) and [Khan Academy](https://www.youtube.com/@khanacademy); use course-page links for the relevant lecture sequence | Same methods as the linked course, with exercises rather than passive viewing | Identify the exact lecture/topic and perform its relevant method on attributed evaluation data; no claim that videos were watched or completed |

MIT, Harvard and Stanford are included for their open materials, not described
as public universities. Public university research/datasets are a separate
category. Neither “all universities” nor “all YouTube” can be exhaustively
searched; this is a bounded set matched to the implemented and remaining gaps.
UC Berkeley is a public university. Its linked course is an archive; the
separately linked textbook is maintained and states a CC BY-SA 4.0 license.
Brady Neal's course is an instructor-hosted resource, not a claim of university
enrollment or accreditation. Free access to any resource here does not imply a
free university credential.

Khan Academy's research and impact pages are separate from its classes.
Published studies must be examined for design, comparator, attrition and outcome
definitions before using their findings. Findings about Khan Academy learners
do not transfer automatically to VessellFramework cyber-range trainees.

See [evaluation methods](evaluation-methods.md) for how these topics connect to
the current rebuild and which claims remain unproven.
