# Research reporting and checkpoint policy

These requirements apply to figures, studies, explanations and handoffs. Existing
project paths and collaboration rules remain authoritative. Use `UNBOUND` for
unknown facts and `not applicable` with a reason for irrelevant fields.

## Figures: meaning, reading guide and conditions

Deliver a figure with a caption and a linked creation record. Together they must
state the question, axes and units, legend or direct labels, meaning of colors,
lines and symbols, and what error bars or bands represent. Explain which features
to compare, what the result supports, and what it cannot establish. A single curve
may use direct labeling instead of a redundant legend.

Record input data identifiers/versions, selections, normalization, model and key
parameters, and uncertainty treatment. Link the plotting script, source revision,
execution record and reproduction command/configuration. Record uncommitted source
changes when relevant; a base commit alone does not identify a modified script.
For a conceptual diagram, describe assumptions and construction method instead of
inventing numerical inputs or error estimates.

Put reading essentials in the figure, interpretation in the caption, and detailed
reproduction conditions in the linked record. Keep large outputs and raw data in
the project's designated storage; commit metadata and locators as appropriate.
Use the figure template or equivalent existing records without duplicating facts.

## Records and commits: meaningful checkpoints

Record work when a study produces a result, an assumption/condition/approach changes,
a failure or uncertainty is discovered, or work is interrupted or handed off.
Capture purpose, change/procedure, conditions, expected and observed result,
evidence references, interpretation/limitations, and the next action. Include
failed and inconclusive attempts. Routine commands need not each create a record;
link detailed execution records instead of copying them.

Commit each coherent, explainable change with its related documentation and
validation records after appropriate checks. Before a long interruption or handoff,
make a checkpoint commit when permitted by the repository workflow. Label unfinished
work and unrun/failed checks explicitly; a checkpoint is not a claim of completion.
Stage only intended changes, preserve unrelated user edits, and exclude secrets,
raw data and generated build products. If a commit is blocked by a concrete rule,
record the reason and remaining diff. Do not create empty commits or commits merely
to meet a time/count quota. Push follows each repository's collaboration and
publication rules; a local commit does not itself authorize a remote publication.

## Explanations: a master's-level reader

Assume a reader with graduate-level fundamentals in the relevant field, but no
knowledge of this project's local conventions. Define project-specific terms,
abbreviations and symbols on first use, including units and sign conventions where
needed. Ordinary vocabulary need not be defined. Add a plain-language explanation
when a specialist term is needed; link a glossary/specification for details while
keeping the immediate explanation understandable on its own.

Explain purpose, method and its rationale, result, then interpretation and limits.
Separate observation, assumption and inference. Keep scientific precision; do not
replace a missing explanation with unexplained jargon. Apply this to captions,
logs, handoffs and user-facing completion reports in the reader's language.

## Completion review

Before reporting completion, check figure explanations and provenance where relevant,
work/study records, first-use definitions, and commit/validation status. Report
remaining gaps explicitly. Structural validators cannot certify readability,
scientific interpretation, or evidence quality; these need a content review.

## Reproduce from inputs and find the evidence

A completed calculation or figure must have enough recorded information for another
person to reproduce it from the original inputs, without relying on chat memory,
unstated local settings or unexplained manual steps. Keep the information necessary
and sufficient for that result; reference existing canonical records rather than
copying everything into every log.

Bind the exact input versions/hashes and access/availability, code revision plus any
uncommitted patch, dependencies/tool versions, environment, configuration, units and
conventions, seeds and stochastic settings where relevant, ordered commands from
setup through calculation/analysis to plotting, and any manual transformations.
Record output locators/hashes and an expected comparison: exact equality when
appropriate, otherwise the numerical/statistical tolerance and its rationale.
If an input, environment or step cannot be recovered, explicitly mark the result
as not yet reproducible and state what is missing. Recording a procedure is not
proof it was rerun; distinguish documented, rerun verified, failed and incomplete.

Connect the research question/decision and Task to its study log, execution record,
Evidence, and result/figure Artifact through stable IDs and repository-relative
links. An Artifact is a saved result or figure; Evidence is the record explaining
what claim was tested; an execution is one run of the procedure. A figure links
its source numerical result and caption/conditions record. Use existing IDs rather
than inventing parallel namespaces. Keep locators/access metadata for externally
stored data and outputs in the repository, not the large files themselves.

Maintain a small human-readable results index, reachable from the project README
(or an existing equivalent entrypoint). Give each result a descriptive title,
IDs, links to its question/Task, execution, evidence and figure record, its output
locator and reproduction status. Update entries when producing or superseding a
result; keep historical links and identify replacements. Detailed conditions stay
in the linked canonical records. Review that links resolve and that a reader can
find a result by topic or ID before reporting completion.
