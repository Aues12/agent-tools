# Documentation Principles

## Purpose

Write repository documentation that helps humans and coding agents understand **what a project is, why it exists, how to use it, and where to find further detail** without reading everything upfront.

Apply these principles proportionally to the project's size, audience, and maturity. They guide documentation decisions; they are not a mandatory file structure or README template.

## Core Principles

1. **Concept before implementation.** Establish purpose, scope, and the reader's mental model before introducing internal files or mechanics.
2. **Progressive disclosure.** Move from a concise overview to usage, architecture, and specialised details as needed. Keep the entry point approachable and deeper references precise.
3. **Minimum sufficient context.** Include enough grounded information for correct understanding, not simply the fewest words or tokens. Remove repetition without removing necessary assumptions or distinctions.
4. **Meaning before procedure.** Explain what a component does and why it matters before detailing how to operate or modify it, where such context is needed.
5. **Summarise and link; do not duplicate.** Give each topic a clear home and direct readers to its authoritative explanation rather than copying it across documents.
6. **Purposeful navigation.** Organise links and sections around reader goals, not merely around the repository's directory tree. A reader should know where to go next.
7. **Shared documentation, different paths.** Human readers and agents may use the same conceptual documentation while following different paths according to their goals or tasks.
8. **Simple from a distance, precise up close.** An overview should be easy to scan; technical details and contracts must remain accurate and accessible.

## README Guidance

Treat the README as an **entry point and navigation hub**, not an exhaustive manual. Where relevant, help the reader answer these questions in approximately this order:

1. **What is this?** A brief, concrete description of the project and its purpose.
2. **Why or when would I use it?** Main capabilities, use cases, and important boundaries.
3. **How do I start?** Installation, prerequisites, and the smallest working example when applicable.
4. **How is it organised?** A short conceptual map of major components or workflows, only if it helps orientation.
5. **Where do I go next?** Links to focused guides, API references, architecture notes, contracts, examples, contributing instructions, or agent guidance, as appropriate.

Adapt, combine, omit, or reorder sections to match the repository. Do not add headings solely to complete a template. Prefer concrete examples over abstract claims, and distinguish implemented functionality from planned work.

## Documentation Navigation

Think of documentation as three complementary structures:

- **Hierarchy:** Where information belongs (project → subsystem → component → implementation).
- **Pathways:** Where someone should go next for a particular goal (learn, use, extend, debug, contribute).
- **Semantic relationships:** Which concepts or documents explain, constrain, depend on, or validate others.

These relationships need not be modelled formally. Clear prose and well-chosen links are often sufficient. Link both toward deeper implementation details and back toward architectural context when it helps interpretation.

## Agent Context

Distinguish between:

- **Meaning context:** Relatively stable purpose, concepts, terminology, architecture, and principles.
- **Task context:** Files, contracts, procedures, tests, and constraints relevant to the current change.

Provide a compact orientation first, then load task-specific detail on demand. If a local task raises architectural uncertainty, return to the broader meaning context before proceeding.

An `AGENTS.md` file can establish essential conventions and route agents to relevant references. It need not reproduce the full documentation set. Keep instructions specific, navigable, and consistent with the actual repository.

## Review Checklist

- Can a new reader explain the project's purpose after the opening section?
- Is the first useful example or next step easy to find?
- Are claims accurate for the current implementation?
- Can readers reach deeper details without reading unrelated material?
- Are links descriptive and authoritative, with little unnecessary duplication?
- Is essential conceptual context preserved while task-specific detail stays local?
- Does each section earn its place for this project's audience?

**Guiding idea:** Standardise clarity and meaningful navigation, not document shapes.
