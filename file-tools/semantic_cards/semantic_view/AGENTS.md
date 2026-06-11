# semantic_view Instructions

## Purpose

`semantic_view` is a lightweight presentation layer for `semantic_cards`.

It turns existing semantic card output into compact, readable, navigable views
for humans and agents.

It must not replace or shrink canonical `semantic_cards` output.

Preferred pipeline:

```text
semantic_ast
  ↓
semantic_cards      canonical / complete / machine-readable
  ↓
semantic_view       compact / readable / navigable
```

The card layer stores semantic truth. The view layer presents that truth.

## Scope

For v1, `semantic_view` accepts ready-made `semantic_cards` output only.

Do not parse source files in this layer.
Do not call `semantic_ast` in this layer.
Do not implement path/source convenience operations in v1.

The caller should first produce cards with one of the existing operations:

```text
build_cards
cards_from_source
cards_from_file
```

Then pass that card result into a view operation.

## Location

Implement inside:

```text
file-tools/semantic_cards/
```

Recommended files:

```text
semantic_view.py
tests/test_semantic_view.py
```

For v1, prefer one `semantic_view.py` file unless it becomes too large.

## Public Operations

Add these operations to the existing `semantic_cards` tool:

```text
summary_view
tree_view
card_view
```

Do not add `generate_cards`; existing card-generation operations already cover
that responsibility.

When operations are added, update:

```text
file-tools/semantic_cards/SKILL.yaml
registry/tool_registry.json
README.md
tests/
```

Follow the repository standard:

* `interfaces` describe access surfaces such as `stdin_json` and `python_api`.
* `operations` describe bounded actions with params, returns, and `available_via`.

## Input Contract

All view operations accept existing semantic card output under `params.cards`.

### summary_view

```json
{
  "operation": "summary_view",
  "params": {
    "cards": { "... semantic_cards result ..." },
    "max_relations": 10
  }
}
```

### tree_view

```json
{
  "operation": "tree_view",
  "params": {
    "cards": { "... semantic_cards result ..." },
    "max_depth": 3,
    "include_statements": false
  }
}
```

### card_view

```json
{
  "operation": "card_view",
  "params": {
    "cards": { "... semantic_cards result ..." },
    "card_id": "function:sample.main"
  }
}
```

## Output Contract

Use the existing tool envelope:

```json
{
  "success": true,
  "message": "Built semantic summary view",
  "result": {},
  "meta": {
    "operation": "summary_view"
  }
}
```

Errors should follow the existing structured style:

```json
{
  "success": false,
  "message": "summary_view requires cards",
  "error": {
    "type": "ValueError",
    "message": "summary_view requires cards"
  }
}
```

Library functions should return plain JSON-serializable dictionaries.
Library functions should not print.
The CLI wrapper may print only the final JSON envelope.

View outputs should be compact.
Do not return the full original card collection from view operations.

## View Types

### summary_view

Purpose: provide a compact overview of the card collection.

It should answer:

* What file/module is this?
* How many modules, classes, functions, blocks, and statements are present?
* What are the top-level semantic units?
* What are the most important relations?

Recommended result shape:

```json
{
  "type": "semantic_summary_view",
  "source": "sample.py",
  "counts": {
    "module": 1,
    "class": 1,
    "function": 3,
    "block": 1,
    "statement": 0
  },
  "top_level": [
    "function:sample.main",
    "class:sample.Example"
  ],
  "relations": [
    "function:sample.main -> function:sample.helper"
  ]
}
```

Default `max_relations` should be `10`.

### tree_view

Purpose: show containment.

Default behavior:

```text
max_depth = 3
include_statements = false
```

Recommended result shape:

```json
{
  "type": "semantic_tree_view",
  "format": "text",
  "tree": "module: sample\n├─ function: main\n└─ class: Example\n   └─ function: run"
}
```

For v1, text tree output is enough and preferred.

Hide statement cards by default. If `include_statements=true`, include them
while still respecting `max_depth`.

### card_view

Purpose: show one semantic card in compact form.

It should include:

* id
* kind
* title
* source location if available
* parent id if available
* visible children
* outgoing relations grouped by kind
* incoming relations grouped by kind if cheap to compute

Recommended result shape:

```json
{
  "type": "semantic_card_view",
  "card_id": "function:sample.main",
  "kind": "function",
  "title": "main",
  "location": "L10-L18",
  "parent_id": "module:sample",
  "children": [],
  "relations": {
    "outgoing": {
      "calls": ["function:sample.helper"]
    },
    "incoming": {}
  },
  "summary": "No summary available."
}
```

If a card has no docstring or useful existing detail, do not invent a summary.
Use:

```text
No summary available.
```

## Design Rules

1. Do not mutate the input card collection.
2. Do not remove or shrink canonical semantic card output.
3. Do not make `semantic_cards` depend on GEO or visualization layers.
4. Do not add visual layout, coordinates, stars, or force simulation here.
5. Do not infer meaning with an LLM.
6. Do not invent summaries when no source/card evidence exists.
7. Preserve source trace when available.
8. Prefer deterministic output.
9. Prefer simple pure functions.
10. Keep tests small and readable.
11. Avoid expression-level noise in default views.

## Suggested Internal Functions

```python
def build_card_index(cards: dict) -> dict:
    """Return card_id -> card mapping."""

def build_children_index(cards: dict) -> dict:
    """Return parent_id -> list[card] mapping."""

def build_relation_index(cards: dict) -> dict:
    """Group relations by source and target card ids."""

def summary_view(cards: dict, max_relations: int = 10) -> dict:
    """Return compact overview of the card collection."""

def tree_view(
    cards: dict,
    max_depth: int = 3,
    include_statements: bool = False,
) -> dict:
    """Return compact containment tree."""

def card_view(cards: dict, card_id: str) -> dict:
    """Return compact view of one semantic card."""
```

Names may be adjusted to match existing code style.

## Testing

Add tests for:

* summary counts
* summary relation cap
* tree rendering without statements
* tree rendering with statements
* max_depth handling
* card lookup by id
* missing card id error
* missing cards input error
* empty card collection
* relation grouping

Use a tiny fixture:

```text
module: sample
├─ function: main
├─ function: helper
└─ class: Example
   └─ function: run

main calls helper
run calls helper
```

Expected default tree:

```text
module: sample
├─ function: main
├─ function: helper
└─ class: Example
   └─ function: run
```

## Future Direction

Later layers may consume these views:

```text
semantic_cards
  ↓
semantic_view
  ↓
observatory_cli
  ↓
GEO / star map
```

Do not implement GEO here.

