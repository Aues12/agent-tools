# Fractal Architecture — Concept Note

## Status
Exploratory concept note, 12 November 2026. A methodology under discussion, not yet a finalized agent instruction.

## Central idea
A system grows from identifiable cores. Each core may be a coherent whole in itself and a part of another whole. Architectural principles recur across scales without requiring identical structures at every scale.

**Fractality means principled self-similarity, not merely nested directories.**

## Relationship to Progressive Disclosure
- **Fractal Architecture** concerns how systems are conceived, differentiated, connected, built, validated, and reorganized.
- **Progressive Disclosure** concerns how their information and structure are presented and navigated without overwhelming the reader.
- **Progressive Elaboration** concerns how an initial idea develops over time.

These approaches complement one another without needing to be inseparable.

## Foundational principles
1. **Core and Identity.** Begin with a purpose-bearing core. A clear name can signal that a coherent whole is recognizable, although naming alone does not establish completion.
2. **Recursive Wholeness.** A component can be complete in its own scope and participate in a larger whole.
3. **Purposeful Differentiation.** Split a system only when a meaningful distinction of responsibility warrants it.
4. **Boundaries and Relations.** Describe what a component does, does not do, and how it relates to other components.
5. **Growth and Refactoring.** Preserve intelligibility while permitting the structure to evolve or be reorganized.
6. **Validation and Completion.** Check a component against its purpose, interfaces, contracts, and behavior, rather than its name alone.
7. **Navigability.** Make the whole comprehensible at a glance and allow deeper inspection when needed.

## Direction of emergence
Growth is **bidirectional**:
- **Top-down:** a larger core differentiates into smaller cores.
- **Bottom-up:** previously independent cores become related and give rise to a newly recognizable higher-level whole.
- **Independence:** a subordinate core may later become an autonomous system.

A hierarchy is therefore not necessarily fixed in advance. It can be discovered, revised, and sometimes replaced by a network of relationships. The tree is useful for navigation; the network can represent cross-cutting semantic relations.

## Example: agent-tools
The first two tools existed before the broader collection took shape. Later tools helped reveal and develop an overarching `agent-tools` identity. This is an example of bottom-up architectural emergence, rather than every tool being designed under a fully predetermined parent architecture.

## Application to code architecture
At repository, package, module, and function scales, consider:
- Purpose and identity
- Scope and boundaries
- Interfaces and dependencies
- Appropriate validation

The same questions recur at different scales, but their concrete implementation should vary with scale. Avoid making every small function a miniature repository.

## Possible working cycle
**Core → Explore → Structure → Validate → Name / Revisit**

This is a tentative cycle, not a mandatory linear procedure. Naming can occur early and be revised; exploration and validation can trigger new cores or reorganize existing ones.

## Open questions
- When is a core sufficiently complete to stand as an independent whole?
- What constitutes an architectural boundary versus a mere conceptual distinction?
- When should a hierarchy be revised to accommodate cross-cutting relations?
- How can an agent propose changes without overriding human judgment?
- What compact operational instructions would translate these principles into reliable repository-building behavior?

## Design intention
Support human-led thinking and construction. The agent may propose possibilities, analyze relationships, implement agreed structures, and validate outcomes; it should not treat its own proposed architecture as authoritative.
