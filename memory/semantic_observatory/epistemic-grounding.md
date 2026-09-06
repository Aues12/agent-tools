# Epistemic Grounding — Target, Claim, Basis, and Return

Status: Active Core. This is a clarification of the Observatory's layered
ontology, not a replacement for its metaphysical foundations.

## Ontological continuity

The Hayy–Kayyum relation gives this project a direction: discovery and living
movement require a form through which they can be held, revisited, and shared.
A record provides that form without claiming to contain the whole meaning.

Ontological principles, epistemic interpretations, engineering models, and
concrete artifacts remain related but distinct. A successful parser does not
prove an ontology; a guiding ontological principle does not certify a parser.
Technical validation concerns the engineering claim made under that principle.

## Target, claim, and localization

An Observation Unit identifies a meaningful target at a chosen scope. Its
smallness is relative to an inquiry: a function may be a unit for architecture,
while one expression or one execution event may be a unit for debugging.

Distinguish:

* **Target:** what is being attended to, such as `parse_file`.
* **Claim:** what is said about it, such as “contains a call named read_file”.
* **Basis:** the source, method, context, or argument supporting that claim.
* **Localization:** the card, graph, text, or image through which it is shown.

A person is a possible observation target; a statement about that person is a
claim. Several claims, including incompatible interpretations, may concern the
same target. One card may gather these without identifying the person with the
card or accepting every claim as true.

## Epistemic status

Use statuses appropriate to the kind of statement rather than a universal
numeric score:

| Kind | What the record should expose |
|---|---|
| Extracted observation | Source snapshot, location, extractor, and analysis limits |
| Derived claim | Inputs and the rule connecting them to the conclusion |
| Heuristic interpretation | Actual hints used, alternatives, and limitations |
| Hypothesis | Proposed explanation and what would prompt reconsideration |
| Symbolic reading | Interpretive tradition, chosen correspondence, and scope |
| Ontological premise | Guiding principle and its place in the conceptual argument |

These are proposed conceptual categories, not an implemented universal claim
schema. They are not a ranking from worthless to valuable. Symbolic readings
can orient inquiry and creation; extracted facts can still be partial or wrong
because their instruments have limits. Determinism establishes repeatability,
not semantic adequacy.

## Observation and interpretation

“Observation precedes interpretation” is a procedural discipline: preserve what
was encountered before committing to an explanatory classification. It does not
require an observer without a viewpoint. The question, selected scope, and
instrument already affect what becomes visible.

For a name-based role label, the function title is evidence of the naming hint.
It is not evidence that the function performs the suggested behavior. A phase
derived from that role cannot acquire stronger warrant merely by being mapped
through a deterministic table.

The current pipeline makes precisely this bounded distinction. It preserves its
legacy display labels while adding their method, basis, candidates, and limits.
See [the pipeline contract](../../file-tools/semantic_observatory_pipeline/README.md).

## Correspondence and disagreement

A correspondence must say what is shared. `same_source_span` connects analysis
nodes over a source region; it does not establish identity of meaning or
behavioral equivalence. A static possible path and an observed execution answer
different questions. A path absent from one trace is not thereby impossible.

The CPG is the shared analysis model for projections. Its internal consistency
does not make it an exhaustive description of the program. Agreement among
projections from one CPG is not independent corroboration.

Before recording a contradiction, compare the target, source snapshot, scope,
and predicates. A changed file, different execution input, or different
analysis coverage may explain a difference without either claim being false.
Unresolved differences should remain visible rather than being forced into one
label.

## Return and revision

An interpretation can be held firmly enough to use and openly enough to revisit.
For a future claim store, preserve the earlier record, record the reason for a
revision, and link the successor to the earlier claim. Do not rewrite the past
as though the new interpretation had always been known.

For now, Git records document revisions, and the analysis payload includes a
hash of the decoded source text. That hash identifies analyzed content; it does
not archive it, identify the analyzer version, prove correctness, or detect
staleness automatically. Keep the source revision and tool revision alongside
saved payloads when reproducibility is required.

## Completion within a horizon

A useful inquiry states its question, relevant scope, available evidence, and
remaining limits. Completion means those stated needs have been met. It does
not mean that all meanings of the target have been enclosed.

Compression should preserve what the inquiry needs, together with a route back
to the source. Every projection should make its selection understandable.

## Authorial grounding

The following user-supplied essays inform this engineering interpretation.
They remain external reading sources, not runtime dependencies. These notes do
not claim that the essays prescribe the exact data fields above.

* [3 Nazarî Katman](../../../ai-agency/first-docs/authors-book/per_post/3-nazari-katman.md): the relation between ontology, mental models, and engineering models supports keeping their contracts distinct.
* [Zanaatkâr’ın İki Eli](../../../ai-agency/first-docs/authors-book/per_post/zanaatkarin-iki-eli.md): flow and a form that can be held motivate preserving exploratory meaning in inspectable artifacts.
* [Hatalardan Dönüş](../../../ai-agency/first-docs/authors-book/per_post/hatalardan-donus.md): revisiting earlier stages and returning to stable ground motivates revision history for interpretations.
* [Mesleklerin Epistemolojisi](../../../ai-agency/first-docs/authors-book/per_post/mesleklerin-epistemolojisi.md): general fields and particular responsibilities inform the distinction between phase and technical role.
* [Ölçüm Manyaklığı](../../../ai-agency/first-docs/authors-book/per_post/olcum-manyakligi-ratio-nal-mania.md): the relation between measurement and its qualitative purpose motivates explicit questions and limits, rather than unsupported confidence numbers.
