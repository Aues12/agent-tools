# Semantic Conventions and Optional Standardization

**Status:** Conceptual design note  
**Scope:** Agent Tools · Semantic Observatory · Semantic Graph  
**Suggested location:** `memory/semantic_observatory/semantic-conventions-and-optional-standardization.md`

## 1. Purpose

This note records a lightweight approach to semantic naming, developer-defined conventions, and optional standardization in Agent Tools and Semantic Observatory.

The central principle is:

> **Conventions should emerge from practice, not precede every possibility.**

The system should preserve semantic openness while offering consistency when consistency is useful. It should not require an exhaustive taxonomy of roles, classes, or node kinds before meaningful analysis can begin.

## 2. Observation: Context Can Produce Coherent Semantic Naming

The `bookbarcode_workflow_dag.json` example illustrates a graph whose node `kind` labels are varied yet intelligible in context. Examples include:

- `input`, `entrypoint`, `orchestration`
- `layout`, `validation`, `encoding`, `core`, `geometry`
- `render`, `io`, `verification`, `artifact`, `output`

Its edge kinds also express meaningful actions and relationships, including `dispatches`, `configures`, `normalizes`, `encodes`, `derives`, `renders`, `verifies`, `installs`, and `envelopes`.

These names need not all belong to a single fixed taxonomy or abstraction level. Their meaning is supported by node labels, graph context, and relationships. The example demonstrates coherent semantic labeling, **not** independent proof that every label faithfully describes the underlying source code.

**Implication:** LLM-based semantic interpretation can propose useful names without a large prescriptive rulebook, provided sufficient context is available.

## 3. Separate Structure from Interpretation

### Structural contract — stable by default

The graph's structural contract should remain explicit and mechanically checkable:

- Unique node identifiers.
- Valid edge endpoints.
- Well-formed input and output data.
- Clear provenance where relevant.
- Validation of declared constraints, such as acyclicity when requested.

These checks protect interoperability and reliability without dictating what a node must mean.

### Semantic vocabulary — open by default

Names such as `kind`, `role`, `phase`, and edge relation kinds should be extensible. A model or developer may introduce a contextually appropriate term when existing vocabulary is insufficient.

A useful distinction is:

- **`kind`** — contextual semantic identity or nature of an observation.
- **`role`** — functional responsibility; may be multiple or mixed.
- **`phase`** — location or participation in an epistemic or processual movement; may span multiple phases.

These are complementary perspectives, not necessarily mutually exclusive classifications. No field should be mandatory merely to satisfy a conceptual taxonomy when it does not improve the representation.

## 4. Developer-Defined Conventions

Developers may optionally declare conventions suited to a repository, domain, or project. Such conventions can help with consistent naming, architectural communication, review, and code generation.

Illustrative configuration (not an implemented Agent Tools schema):

```yaml
semantic_conventions:
  enabled: true
  roles:
    Validator:
      suggested_names: ["validate_*", "check_*"]
      expectations:
        - "Report validation failures clearly"
        - "Avoid unrelated file mutations"
    Transformer:
      suggested_names: ["transform_*", "normalize_*"]
      expectations:
        - "Make input-output behavior understandable"
```

Such conventions are **project-defined preferences**, not universal laws. A function can legitimately perform validation without starting with `validate_`; naming heuristics are evidence, not conclusive proof of behavior.

The developer should be able to enable, modify, ignore, or remove conventions without changing the underlying graph contract.

## 5. Optional Standardization

Standardization should respond to demonstrated need, not become a prerequisite for exploration.

A lightweight path is:

1. **Discover:** A developer or LLM proposes meaningful names and relationships from context.
2. **Validate structure:** Deterministic checks verify graph integrity and applicable technical constraints.
3. **Review when useful:** A human examines ambiguous, novel, or consequential interpretations.
4. **Standardize selectively:** Repeated, useful patterns may become documented conventions or reusable vocabulary.
5. **Revisit:** Conventions remain versioned and revisable as practice evolves.

Not every discovered label requires admission to a registry. A local or one-off term may remain local.

## 6. Deterministic and LLM Interpretations

The two forms of analysis may coexist without overwriting each other:

- **Deterministic analysis:** structural facts, declared rules, detectable patterns, and inexpensive heuristics.
- **LLM interpretation:** contextual purpose, possible roles, mixed responsibilities, novel kinds, and explanations.
- **Developer declaration:** intended design, selected conventions, and human review or correction.

A Semantic Card may display these perspectives side by side. Differences should be inspectable rather than silently resolved into one supposedly authoritative label.

Suggested conceptual fields (not a required schema):

```text
Observation
  ├── structural evidence
  ├── developer declarations
  ├── deterministic classifications
  ├── LLM interpretations
  ├── supporting evidence and provenance
  └── optional reconciliation / review status
```

LLM output should be guided by **lightweight quality expectations** rather than an exhaustive vocabulary: stay grounded in available evidence, distinguish observations from interpretations, allow uncertainty, and permit new or mixed categories.

## 7. From Observation to Construction

The same conventions can eventually guide code creation as well as code inspection:

```text
Observe existing code
    ↓
Interpret semantic structure
    ↓
Identify useful recurring patterns
    ↓
Optionally document conventions
    ↓
Design cards / blueprints
    ↓
Generate or edit code
    ↓
Observe again
```

This is compatible with the Semantic Architecture direction of **Observation** (`Source → AST → Cards → Observatory`) and **Construction** (`Blueprint → Cards → Source Synthesis → Code`).

A convention can assist an agent in producing code aligned with a developer's preferred style. It should not prevent the discovery of better structures or new semantic roles.

## 8. Design Guardrails

- **Avoid taxonomy inflation.** Do not add categories merely for completeness.
- **Avoid bureaucratic overhead.** Introduce rules only when they solve recurring problems.
- **Keep provenance visible.** A developer declaration, heuristic result, and LLM interpretation are different kinds of claims.
- **Do not confuse naming with correctness.** A plausible `kind` is not proof of actual behavior.
- **Allow multiplicity and novelty.** Mixed roles, multiple phases, and previously unseen patterns should remain expressible.
- **Prefer optionality.** More demanding conventions can be enabled for projects that benefit from them.
- **Preserve human agency.** Developers decide whether an inferred pattern becomes a local or shared convention.

## 9. Guiding Principle

> **Keep the structural contract stable, the semantic vocabulary open, and standardization optional.**

The aim is not to make the model obey an ever-growing rulebook. It is to make useful semantic discoveries understandable, inspectable, reusable, and—only when needed—stable enough to guide future work.

---

**Related notes:** `role-system-conversation.md`, `semantic-architecture.md`, `semantic-workbench.md`, `semantic-cards.md`, `epistemic-phases-and-roles.md`.
