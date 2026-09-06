# Phase Interpretation Contract

Status: Active Bridge. This note governs the move from symbolic research to
engineering claims. It does not implement a symbolic classifier.

## Preserve the levels

The four elements and their traditional correspondences provide a meaningful
orientation for this project. Their ontological treatment remains in the
foundations and symbolic research notes. A particular assignment of an element
to a function is a further interpretive act and needs its own explanation.

The question “what portion of the ring is visible?” is appropriate when a ring
has been adopted as an interpretive frame. It must not silently establish that
a static analyzer has detected every phase.

## Separate the axes

The research notes use elemental vocabulary across several related axes:

| Axis | Example | Necessary context |
|---|---|---|
| Epistemic activity | Discovery, Understanding | Inquiry or workflow |
| Technical role | Parser, Builder | Component responsibility |
| Artifact state | Intermediate representation, persisted result | Lifetime and enclosing process |
| Symbolic correspondence | Air, Water | Interpretive frame and rationale |
| Modality | Initiating, sustaining, adapting | Movement being described |

An AST may be a finished result within a parser and intermediate material within
a larger workflow. This is a change of observational scope, not a contradiction.
Likewise, Water as understanding and Water as transmission should name their
respective interpretive contexts rather than overwrite one universal enum.

The existing pipeline's `phase` field means only the four epistemic activity
labels used for card display. It does not encode artifact state, modality,
elemental identity, or detected ring membership. `phaseSymbols` is a display
mapping and adds no independent evidence.

## Rings and visibility

Preserve the reference sequence Earth → Fire → Air → Water → Earth as a symbolic
reading. In any future analyzer distinguish:

* observed stages and their source locations;
* inferred or interpretively supplied stages and their rationale;
* stages outside the inspected scope;
* stages for which the available analysis has no determination.

For `return a + b`, a visible operation and returned result do not independently
establish hidden Air and Water stages. A symbolic expansion may supply them,
but should carry that status. An unknown technical assignment does not deny the
ontological principle; it describes the instrument's current reach.

Do not implement a single `4/4` score that conflates phases present, transitions
visible, and a symbolically completed ring. Any future coverage metric must
name its counted units and distinguish observation from interpretive completion.

## Promotion to an executable classifier

Before adding symbolic inference to tools:

1. State the observation scope and exact question the classifier answers.
2. Define which input evidence supports each assignment.
3. Include ambiguous and unclassified outcomes.
4. Test names that disagree with behavior, nested scopes, partial processes,
   and cases outside the instrument's coverage.
5. Preserve technical analysis separately from interpretive annotations.
6. Record what would change an assignment, without pretending the test settles
   the underlying metaphysical principle.

Current name-based display metadata is a limited interim instrument. Its
candidate list reports competing keyword matches, not competing proven
responsibilities. Empty candidates mean no keyword match (or a kind-based
rule), not an absence of meaning.

See [Epistemic Grounding](epistemic-grounding.md) for target, basis, and revision,
and [Implementation Map](implementation-map.md) for the current tool boundary.
