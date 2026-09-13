# semantic_observatory_pipeline

`semantic_observatory_pipeline` runs existing semantic tools and adapts their
outputs for Semantic Observatory UI.

```txt
source.py
  -> semantic_ast
  -> semantic_cards
  -> semantic_dfg
  -> semantic_cpg
  -> Flat View UI data
```

## CLI

```bash
python3 file-tools/semantic_observatory_pipeline/semantic_observatory_pipeline.py <<'JSON'
{
  "operation": "analyze_source",
  "params": {
    "path": "example.py",
    "source": "def add(a, b):\n    return a + b\n"
  }
}
JSON
```

## Python API

```python
from tool import analyze_source

result = analyze_source("def add(a, b):\n    return a + b\n", path="example.py")
```

The returned result includes canonical artifacts under `artifacts` and UI-ready
data under `ui`.

Current artifacts:

```txt
semantic_ast      structural localization
semantic_cards    card/interface localization
data_flow_graph   local value-flow localization
semantic_cpg      unified analysis graph for projection layers
```

Flat View UI data is still adapted from semantic cards and DFG enrichment. The
CPG is included for future projection layers such as flowchart, map, and
geometric views.

By default the pipeline requests Flat View friendly card generation:

```txt
include_statements = false
include_blocks     = false
```

This means generated Semantic Observatory analysis omits low-level statement
cards and control-flow block cards such as `if`, `try`, and `except_handler`.

## Role and Phase Metadata

Flat View `role` and `phase` values are currently deterministic UI metadata.

`role` is inferred from card kind and simple title keywords such as `parse`,
`build`, `validate`, `render`, and `run`.

`phase` is then derived from role through a fixed mapping:

```txt
Explorer / Locator      -> Discovery
Parser / Analyzer       -> Understanding
Transformer             -> Transformation
Builder / Renderer      -> Manifestation
```

This is not symbolic phase inference. It is a temporary presentation adapter
until deeper phase classification is introduced.

## Classification provenance

Every UI card retains its existing `role` and `phase` strings and adds
`classification` with:

* `method`: `flat_view_role_phase_v1`, identifying the ordered rule set.
* `scope`: `card_display`; `targetId`: the associated card identifier.
* `role`: `value`, `status` (`heuristic` or `fallback`), `basis`, `evidence`,
  ordered `candidates`, and `ambiguous`.
* `phase`: `value`, `status: derived`, `basis: role_mapping`, `dependsOn: role`.
* `limitations`: statements limiting what these labels establish.

Role `basis` is `card_kind`, `statement_title`, `title_substring`, or `fallback`.
Evidence contains the supplied kind and title. Name matching retains the
existing case-insensitive substring behavior and rule precedence. For example,
`read_and_build` displays Parser and Understanding but records both Parser/read
and Builder/build candidates, with `ambiguous: true`. A name with no matching
keyword is explicitly marked as a fallback. Candidate absence is not evidence
of an absence of meaning. No numeric confidence is asserted.

Canonical `artifacts.semantic_cards` remain unannotated. The adapter does not
mutate its inputs. These additive fields are available to API consumers; the
current Flat View does not yet present the full classification record.

## Source snapshot identity

`analyze_source` and `analyze_file` include `source.contentHash`, the SHA-256 hex
digest of the analyzed string encoded as UTF-8, and
`source.hashBasis: sha256:utf8-decoded-source`. It is independent of display path.
For file analysis the string follows the selected decoding and Python text
reading's newline normalization; this is not a hash of original file bytes.
The hash covers source text, not analysis options or tool versions.

A fingerprint identifies content, not its correctness. It neither archives the
source nor automatically checks for staleness. Consumers saving individual
cards should retain the parent source record alongside them. Standalone
`adapt_for_ui` has no source text and therefore emits no source fingerprint.

See [Epistemic Grounding](../../memory/semantic_observatory/epistemic-grounding.md).
