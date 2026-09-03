# Graph models

## Purpose

Build a composable taxonomy of graph models from the most general and least
constrained form toward specialized structures. The taxonomy should help an
agent choose a model deliberately without forcing every useful combination
into a rigid inheritance tree.

Inclusion here does not imply implementation. This document separates:

```text
carrier structure  = what can be connected
structural axes    = how connections behave
constraints        = which graph shapes are valid
enrichments        = what extra data elements carry
profiles           = what the graph means in a domain
```

## Why a composable taxonomy

A single tree such as `Graph -> DirectedGraph -> DAG -> Tree` explains one
specialization path, but it cannot place every graph cleanly. A graph may be
directed, allow parallel edges, carry weights, and vary over time at once.
Those properties are largely independent.

The four common NetworkX containers already separate direction from edge
multiplicity: `Graph`, `DiGraph`, `MultiGraph`, and `MultiDiGraph`. Self-loops
are allowed in all four, while only the `Multi*` variants admit parallel
edges. This is useful evidence that direction and multiplicity should be
modeled as separate axes rather than one deep class hierarchy. See the
[NetworkX graph type reference](https://networkx.org/documentation/stable/reference/classes/index.html).

## Taxonomy overview

```text
Graph document
│
├── Carrier
│   ├── binary graph: each edge connects two nodes
│   └── hypergraph: one edge may join many nodes
│
├── Orientation
│   ├── undirected
│   ├── directed
│   └── mixed
│
├── Multiplicity
│   ├── simple
│   └── multi
│
├── Local edge policy
│   ├── self-loops allowed / forbidden
│   └── parallel edges allowed / forbidden
│
├── Global shape constraints
│   ├── acyclic
│   ├── connected
│   ├── rooted
│   ├── parent-limited
│   └── bipartite
│
├── Enrichments
│   ├── labels and open kinds
│   ├── properties
│   ├── weights or signs
│   ├── temporal validity
│   └── uncertainty or confidence
│
└── Domain profiles
    ├── dependency
    ├── workflow
    ├── state transition
    ├── hierarchy / taxonomy
    ├── knowledge
    ├── causal
    └── assignment / matching
```

The groups above `Domain profiles` describe structure or reusable enrichment.
Profiles are discussed separately because the same composition can support
several domain meanings.

## Level 0 — graph document and identity

Before selecting a mathematical model, the tool needs a durable container.
The graph document supplies identity and storage metadata without changing the
graph's topology.

Provisional minimum:

```json
{
  "graph_id": "bookbarcode-flow",
  "title": "BookBarcode generation flow",
  "revision": 4,
  "next_node_id": 6,
  "next_edge_id": 5,
  "model": {},
  "nodes": [],
  "edges": []
}
```

`graph_id` is stable machine identity; `title` is mutable display text. Nodes
and edges have independent, monotonically increasing graph-local integer IDs.
This document layer applies to every later model.

## Level 1 — ordinary binary graph

The simplest useful carrier contains nodes and binary edges. A binary edge
connects two endpoints. At this level, the semantic meaning of the endpoints
and relation remains open.

Minimum capabilities:

* add and inspect nodes;
* add and inspect edges;
* validate identity and endpoint existence;
* preserve open `kind` values and JSON-compatible attributes;
* serialize without losing identity or order.

Potential uses:

* free-form idea maps;
* entity and relationship capture;
* small research notebooks;
* agent-created context sketches;
* a neutral interchange form before a stricter model is selected.

The ordinary graph should impose as few topological constraints as practical.
Direction, parallel edges, and self-loops must still be represented explicitly
in its model description so consumers do not have to guess.

## Level 2 — orientation

### Undirected graph

An edge expresses a symmetric connection: `A -- B`. Reversing its endpoints
does not create a different relationship.

Potential uses:

* peer or collaboration networks;
* mutual compatibility;
* physical adjacency;
* similarity relationships;
* infrastructure links when flow direction is irrelevant.

Useful capabilities include connected components, neighborhoods, paths, and
clusters.

### Directed graph

An edge has a source and target: `A -> B`. Reversing it changes the statement.

Potential uses:

* process progression;
* dependencies;
* state transitions;
* influence or causation claims;
* hyperlinks and references;
* producer-consumer relations.

Useful capabilities include predecessors, successors, reachability, and cycle
detection.

### Mixed graph

A mixed graph contains both directed and undirected relations. It is useful
when one domain genuinely combines asymmetric and symmetric connections.

Potential uses:

* organizations containing both reporting lines and peer collaboration;
* transport maps containing one-way and two-way links;
* knowledge maps mixing directed claims with symmetric similarity.

Mixed direction likely requires edge-local orientation and complicates
traversal. It should be researched now but deferred until a concrete workflow
cannot be modeled clearly with one graph-wide orientation.

## Level 3 — multiplicity and loops

### Simple graph

A simple graph permits at most one structural edge for a given endpoint pair
under its orientation rules. Whether two semantically different `kind` values
count as parallel edges must be stated explicitly by the tool contract.

Potential uses:

* minimal dependency maps;
* trees and simple hierarchies;
* networks where only existence of a relation matters.

### Multigraph

A multigraph permits distinguishable parallel edges between the same endpoint
pair. Stable edge identity becomes essential.

```text
Alice -[reports_to: edge 1]-> Bob
Alice -[mentored_by: edge 2]-> Bob
```

Potential uses:

* transport routes with several services between the same locations;
* repeated events or communications;
* multiple evidence statements supporting the same pair;
* relationships that differ by role, source, or time;
* property-graph workloads.

### Self-loop policy

A self-loop connects a node to itself. It is not inherently invalid.

Potential uses:

* a state transition that returns to the same state;
* recursive dependencies;
* self-reference;
* repeated activity in a process model.

Trees and DAGs must forbid self-loops because a self-loop is a cycle. Other
models should make the policy explicit instead of rejecting loops globally.

## Level 4 — global shape constraints

These models specialize a carrier by restricting the complete topology.

### Directed acyclic graph

A DAG is directed and contains no directed cycle. This constraint enables
topological ordering, generations, ancestor/descendant queries, transitive
closure or reduction, and longest-path analysis. The
[NetworkX DAG reference](https://networkx.org/documentation/stable/reference/algorithms/dag.html)
lists these as DAG-oriented capabilities and also notes that callers must not
assume every algorithm performs its own acyclicity check.

Potential uses:

* build and package dependencies;
* prerequisite maps;
* data-processing pipelines;
* provenance chains;
* staged approval processes with no return transitions;
* task plans in which circular dependency is an error.

The model should validate acyclicity when selected. It should not silently
coerce a cyclic directed graph into a DAG.

### Forest and tree

An undirected forest is acyclic; an undirected tree is a connected forest.
Directed terminology has competing conventions, so the tool should avoid a
bare `directed_tree` name until root and parent rules are explicit. NetworkX,
for example, distinguishes directed forests, branchings, and arborescences in
its [tree reference](https://networkx.org/documentation/stable/reference/algorithms/tree.html).

Potential uses:

* file and folder hierarchy;
* organization charts;
* classification trees;
* document outlines;
* decision trees;
* agent plan decomposition.

A rooted outward hierarchy is more precisely described by constraints such as:

```text
directed
acyclic
exactly one root
root in-degree = 0
every other node in-degree = 1
all nodes reachable from root
```

This explicit constraint set is preferable to relying on an ambiguous model
name.

### Bipartite graph

A bipartite graph partitions nodes into two sets and allows edges only between
opposite sets. NetworkX represents this using ordinary `Graph` or `DiGraph`
containers plus a node partition attribute rather than a separate graph class;
see its [bipartite graph reference](https://networkx.org/documentation/stable/reference/algorithms/bipartite.html).
This is strong evidence that bipartite behavior can be a constraint/policy over
a base graph rather than a mandatory subclass.

Potential uses:

* people to projects;
* candidates to jobs;
* tests to requirements;
* resources to tasks;
* authors to publications;
* customers to products;
* matching and allocation problems.

Required additional data is a partition identity on every node, plus validation
that no edge connects nodes in the same partition.

### Connected graph

Connectivity is often a validation option rather than a standalone stored
model. It is useful when isolated components indicate incomplete authoring.

Potential uses:

* one coherent process map;
* a single taxonomy tree;
* a route or infrastructure network expected to be traversable.

Disconnected graphs remain legitimate for research corpora, forests, separate
communities, and incomplete workspaces.

## Level 5 — element enrichments

Enrichments add data without necessarily changing which topologies are valid.

### Labeled and typed graph

Nodes and edges carry human labels and open semantic kinds. This should be part
of the practical `semantic_graph` foundation because an agent needs meaningful
handles even when no profile is active.

```json
{
  "unique_id": 2,
  "kind": "validation_step",
  "label": "Validate ISBN"
}
```

Kinds remain open at the core level. A profile may later recommend or constrain
them.

### Attributed or property graph

Nodes and edges carry key/value properties. Apache TinkerPop describes a
property graph as a directed, binary, attributed multigraph and separates graph
structure from traversal/process. Its structure includes vertices, edges,
labels, and properties; see the
[TinkerPop reference](https://tinkerpop.apache.org/docs/current/reference/#graph-computing).

Potential uses:

* domain entities with metadata;
* project and task state;
* catalog and inventory relations;
* social or organizational networks;
* evidence-rich context graphs;
* graph database interchange.

`semantic_graph` should learn from the property-graph separation of structure
and process without adopting the entire database model. Optional JSON
attributes are sufficient for the early tool.

### Weighted graph

A numeric value on an edge or node represents cost, distance, capacity,
priority, similarity, or another domain quantity.

Potential uses:

* route cost;
* task effort;
* dependency strength;
* recommendation ranking;
* network capacity.

The core can store a `weight` attribute without interpreting it. A profile must
define its meaning, unit, allowed range, and whether lower or higher is better
before weighted algorithms are trustworthy.

### Signed graph

An edge sign represents positive/negative, support/opposition, trust/distrust,
or activation/inhibition.

Potential uses:

* argument maps;
* sentiment or trust networks;
* regulatory biology;
* supporting and contradicting evidence.

Like weights, signs are easy to store but require profile semantics before
analysis.

## Level 6 — temporal and uncertain models

### Temporal graph

Nodes or edges are active at instants or over intervals. A static projection can
lose causal order and produce paths that never existed in time. The temporal
network literature emphasizes that activation timing changes reachability and
diffusion behavior; see Holme and Saramäki's
[Temporal Networks review](https://arxiv.org/abs/1108.1780).

Potential uses:

* communications and meetings;
* changing organizations;
* project history;
* event and audit trails;
* transport schedules;
* evolving knowledge or evidence.

Early graphs may store temporal fields as attributes. A true temporal model is
needed only when the tool must validate intervals or calculate time-respecting
paths.

### Uncertain or probabilistic graph

Nodes, edges, or semantic claims carry confidence or probability.

Potential uses:

* LLM-inferred context;
* incomplete research evidence;
* hypotheses;
* risk and scenario modeling;
* uncertain entity resolution.

Confidence metadata must not be confused with mathematical probability unless
a profile defines calibration and combination rules. The core should preserve
the value, not reason from it.

## Level 7 — higher-arity carrier

### Hypergraph

An ordinary binary edge relates two nodes. A hyperedge can relate more than two
nodes as one atomic relationship. HyperNetX describes hypergraphs as models for
multi-way relationships where ordinary graphs capture only two-way relations;
see the [HyperNetX overview](https://hypernetx.readthedocs.io/en/latest/).

Potential uses:

* one meeting involving several participants;
* a paper with multiple authors;
* a chemical reaction involving several substances;
* a constraint involving several variables together;
* team membership or group events.

This model does not fit the current `source`/`target` edge schema without either
lossy conversion or a new endpoint representation. It should be deliberately
deferred rather than simulated invisibly. A bipartite incidence projection can
represent a hypergraph when interoperability is needed, but that projection is
not identical to the original model.

## Level 8 — semantic data models

### RDF graph

RDF represents information as subject-predicate-object triples and treats an
RDF graph as a set of such triples. The current W3C RDF 1.2 specification also
distinguishes datasets containing a default graph and named graphs. See
[RDF 1.2 Concepts and Abstract Data Model](https://www.w3.org/TR/rdf12-concepts/).

Potential uses:

* interoperable linked data;
* web-scale identifiers;
* metadata exchange;
* data integration across independently maintained vocabularies.

RDF predicates and identity rules are stricter than an open property graph.
RDF compatibility should therefore be an explicit model/export layer, not a
claim made about every `semantic_graph` artifact.

### OWL ontology

OWL adds formally defined ontology semantics over classes, properties,
individuals, and axioms. It can support machine reasoning beyond traversing
explicit edges. See the [W3C OWL 2 overview](https://www.w3.org/TR/owl-overview/).

Potential uses:

* formal domain vocabularies;
* interoperability rules;
* consistency checking by ontology reasoners;
* deriving implicit classifications.

OWL is outside the early `semantic_graph` scope. The graph core should not
imply formal semantics merely because nodes and edges have kinds.

## Model versus profile examples

The following are usually better treated as profiles built from structural
models:

| Profile | Likely model composition | Domain meaning |
|---|---|---|
| Dependency graph | directed + usually acyclic | one item requires another |
| Workflow graph | directed + possibly cyclic + properties | control or work progresses |
| State transition graph | directed + self-loops allowed | events change state |
| Taxonomy | rooted directed acyclic hierarchy | broader/narrower classification |
| Organization chart | rooted hierarchy + properties | reporting responsibility |
| Knowledge graph | directed property/multi graph | typed domain claims |
| Causal graph | directed; DAG in many methods | asserted causal influence |
| Assignment graph | bipartite + optionally weighted | candidates connect to choices |

The table is a starting hypothesis. Each profile must state its actual
constraints rather than inherit them from its name.

## Proposed research representation

Instead of one class name carrying every feature, a model can be described by
orthogonal fields:

```json
{
  "carrier": "binary",
  "orientation": "directed",
  "multiplicity": "multi",
  "self_loops": false,
  "constraints": ["acyclic"],
  "enrichments": ["labels", "properties", "weights"]
}
```

This is not yet a stable schema. It is a research device for testing whether
models compose cleanly. A public API may later provide convenience classes such
as `DirectedGraph` or `DAG` while serializing the explicit structural choices.

## Suggested implementation horizon

### Horizon A — general practical core

* graph document identity;
* separate monotonic node and edge IDs;
* binary nodes and edges;
* explicit direction policy;
* explicit parallel-edge and self-loop policies;
* labels, open kinds, and attributes.

### Horizon B — common validators and views

* DAG validation and topological ordering;
* connected-component inspection;
* rooted hierarchy/tree validation;
* bipartite partition validation;
* bounded neighborhood and path views.

### Horizon C — domain-neutral enrichments

* weights and units;
* signed relations;
* temporal validity;
* uncertainty metadata.

### Horizon D — alternate carriers and interoperability

* hyperedge representation;
* RDF import/export;
* ontology-aware integration only if a concrete workflow needs reasoning.

## Selection questions for an agent

Before creating a graph, an agent should eventually be able to ask:

1. Does relation direction matter?
2. Can the same endpoints have several distinct relationship instances?
3. Are self-relations meaningful?
4. Are cycles valid, invalid, or unknown?
5. Must all nodes belong to one connected structure?
6. Is there a root or parent-count rule?
7. Are nodes divided into partitions?
8. Do properties, weights, time, or confidence affect interpretation?
9. Does one relation need more than two endpoints?
10. Is formal linked-data or ontology interoperability required?

The least constrained model that preserves the required meaning should be
preferred.

## Sources

* [NetworkX graph types](https://networkx.org/documentation/stable/reference/classes/index.html)
* [NetworkX directed acyclic graph algorithms](https://networkx.org/documentation/stable/reference/algorithms/dag.html)
* [NetworkX tree definitions](https://networkx.org/documentation/stable/reference/algorithms/tree.html)
* [NetworkX bipartite graph reference](https://networkx.org/documentation/stable/reference/algorithms/bipartite.html)
* [Apache TinkerPop graph structure and process](https://tinkerpop.apache.org/docs/current/reference/#graph-computing)
* [W3C RDF 1.2 Concepts and Abstract Data Model](https://www.w3.org/TR/rdf12-concepts/)
* [W3C OWL 2 overview](https://www.w3.org/TR/owl-overview/)
* [HyperNetX overview](https://hypernetx.readthedocs.io/en/latest/)
* [Holme and Saramäki, Temporal Networks](https://arxiv.org/abs/1108.1780)
