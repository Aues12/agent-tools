# compression

Semantic compression and LLM-oriented AST reduction utilities.

This module transforms semantic AST structures into:
- compact
- high-signal
- LLM-friendly
representations.

The goal is not syntactic completeness,
but semantic density.

---

# Core Philosophy

Raw AST structures contain large amounts of low-level detail.

Most agent and LLM workflows do not require:
- parser internals
- syntax metadata
- verbose nesting
- transport noise

This module reduces structural noise while preserving semantic meaning.

---

# Purpose

The compression layer exists to improve:
- token efficiency
- readability
- retrieval quality
- semantic navigation
- local model performance

The output should expose:
- what the code does
- what structures exist
- how components relate

without unnecessary parser complexity.

---

# Compression Philosophy

Prefer:
- semantic meaning
- compact structures
- stable schemas
- deterministic reduction
- high signal-to-noise ratio

Avoid:
- excessive nesting
- parser-specific verbosity
- unnecessary metadata
- redundant syntax details

---

# Typical Transformation

Example:

Raw semantic node:

```json id="jlwm4x"
{
  "type": "name",
  "id": "x",
  "context": "Load",
  "line": 5
}
```

Compressed form:

```json id="jlwm0a"
"x"
```

The goal is preserving meaning,
not preserving every parser detail.

---

# Architectural Role

Typical pipeline:

```text
source code
    ↓
AST
    ↓
semantic_ast
    ↓
compression
    ↓
LLM / runtime / retrieval
```

This module acts as a semantic optimization layer.

---

# Intended Use Cases

Examples include:
- LLM context compression
- local model optimization
- semantic indexing
- retrieval pipelines
- repository summarization
- lightweight code navigation
- semantic search preprocessing

---

# Determinism

Compression should remain deterministic.

The same semantic AST input should produce the same compressed output.

No probabilistic reasoning or LLM inference should occur during compression.

---

# Layer Separation

This module should NOT:
- parse source code directly
- execute code
- perform runtime orchestration
- replace semantic_ast parsing

Responsibilities should remain separated:

```text id="jlwm6w"
semantic_ast = structure extraction
compression = semantic reduction
```

---

# Compression Strategy

Compression should be:
- node-aware
- structure-aware
- semantics-first

Different node types may require different compression strategies.

Example:
- functions → summarized by name/calls/args
- classes → summarized by methods/bases
- imports → summarized by module names

---

# Metadata Philosophy

Preserve metadata only when it meaningfully improves:
- navigation
- retrieval
- orchestration
- code extraction

Prefer minimal useful metadata.
