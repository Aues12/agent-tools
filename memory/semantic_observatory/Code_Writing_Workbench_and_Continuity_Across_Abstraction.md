# Code Writing Workbench & Continuity Across Abstraction

*Concept notes — 12 November 2026*

## 1. Code Writing Workbench

### Purpose
A human-led, LLM-assisted programming environment in which conceptual architecture is defined before implementation. The human establishes core identities, purposes and architectural decisions; the model proposes refinements, specifications, contracts and code for review.

### Interface
- **Architecture tree first:** The primary navigation surface represents conceptual cores and subcores, not directories.
- **Optional graph view:** Displays cross-cutting dependencies and relationships that cannot be expressed adequately as a tree.
- **Zoomable infinite canvas:** Allows movement across project, architecture, module and source-code levels.
- **Semantic zoom:** Different levels of zoom reveal different kinds of information, rather than merely scaling the same drawing.
- **Shared architecture model:** Tree, canvas and code views reflect the same underlying entities and relationships.
- **Implementation mapping:** A core may map to multiple files, and a file may contribute to multiple cores; the conceptual architecture must not be reduced to the file tree.

### Development workflow
Human Intent → Architecture → Specification → LLM Implementation → Validation → Human Review.

This workflow is iterative, not rigidly linear. A discovery in a lower-level core may require revisiting a higher-level architectural decision. The model suggests expansions and explains their rationale; the human can approve, modify or reject them.

### Initial prototype
1. Define and name a core.
2. Ask the LLM to propose subcores, responsibilities and boundaries.
3. Review and approve the architecture.
4. Generate implementation code for an approved core.
5. Inspect the implementation through the corresponding architecture node and validate it against contracts and tests.

The first version need not reproduce a full IDE. A read-only code viewer and a focused implementation pipeline are sufficient to test the method.

## 2. Continuity Across Abstraction

### Principle
**A component's identity, purpose, boundaries and relationships should remain traceable from its conceptual core through architectural layers to its concrete implementation and tests.**

### Implications
- **Conceptual identity is not file structure.** A core is defined by its responsibility and meaning, not its directory path.
- **Abstraction does not imply disconnection.** Project, architecture, module and code views describe related aspects of the same system.
- **Navigation does not require information overload.** The user can inspect the whole at a high level and progressively disclose details as needed.
- **Traceability is bidirectional.** Users should be able to move from a core to its code and from code back to the architectural decisions that explain it.
- **Architectural evolution is bidirectional.** Cores can differentiate into subcores, combine into a new encompassing whole, or become independent systems.
- **Validation crosses levels.** Implementation correctness and architectural consistency should both be checked.

### Relationship to other principles
- **Fractal Architecture:** How coherent systems and sub-systems are formed and evolved.
- **Progressive Disclosure:** How complexity is revealed incrementally to the reader or user.
- **Continuity Across Abstraction:** How meaning and identity remain connected while moving between levels.

### Open design questions
- How should core-to-code mappings be represented and kept synchronized?
- What distinguishes a core's conceptual completion from its implementation completion?
- Which semantic-zoom transitions should be automatic, and which should require explicit navigation?
- How should cross-cutting relationships appear without obscuring the primary tree hierarchy?
