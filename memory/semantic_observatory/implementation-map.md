# Semantic Observatory Implementation Map

This document maps Semantic Observatory concepts to the current agent-tools
implementation.

The goal is to keep conceptual language and executable tools aligned.

## Concept to Implementation

```text
Conceptual Layer        Implementation
---------------------------------------------------------------
Observation Unit        function, class, module, or card target
Localization            source, AST, call_graph, data_flow_graph, card, view
Structural Localization semantic_ast
Relation Localization   call_graph, semantic_dfg
Value-flow Localization semantic_dfg
Interface Localization  semantic_cards
Observation Pipeline    semantic_observatory_pipeline
Presentation View       semantic_view
Depth                   AST containment depth
Level                   call graph height
Flow Level              DFG value-flow distance
Role                    parser, builder, transformer, validator etc.
Phase                   discovery, understanding, transformation, manifestation
Quest                   guided traversal or query plan
Geometry                future visual localization
```

## Tool Alignment

```text
semantic_ast   = structural localization
call_graph     = function relation localization
semantic_dfg   = value-flow localization
semantic_cards = card/interface localization
semantic_observatory_pipeline = executable analysis pipeline for UI-ready data
semantic_view  = presentation localization
```

## Code Card Alignment

For code analysis, a source object such as a function, class, or module is the
observation target.

A Semantic Card is a localized interface to that target.

`depth`, `level`, and `flow_level` should not be collapsed:

```text
depth      = where the target sits in the containment structure
level      = how much of the function-call relation graph lies beneath the target
flow_level = how far a value sits downstream in a local data-flow graph
```

For Python code:

```text
card depth comes from semantic AST traversal
card level comes from local call graph height
DFG node depth comes from local structural nesting inside a function
DFG node flow_level comes from local value-flow distance
```

Example:

```text
price, quantity -> subtotal -> tax -> total -> return_value

price        flow_level 0
subtotal     flow_level 1
tax          flow_level 2
total        flow_level 3
return_value flow_level 4
```

## Role and Phase

Role is a technical classification.

Phase is an epistemic classification.

Examples:

```text
Role        Phase
-------------------------------
locator     discovery
parser      understanding
analyzer    understanding
validator   understanding
transformer transformation
aggregator  transformation
builder     manifestation
renderer    manifestation
executor    manifestation
```

Cards may eventually carry both fields:

```json
{
  "kind": "function",
  "role": "builder",
  "phase": "manifestation",
  "depth": 1,
  "level": 4
}
```

## Design Rule

Conceptual layers should guide implementation, but not replace concrete tool
contracts.

Tools should still expose explicit inputs, outputs, side effects, and validation
rules.
