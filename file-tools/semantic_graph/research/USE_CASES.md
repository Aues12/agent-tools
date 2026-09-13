# Potential use cases

## Purpose

Test the graph-model taxonomy against coding and non-coding domains. The goal
is not to create profiles yet; it is to discover which structural capabilities
the general model must preserve.

The mappings below are design hypotheses for pressure-testing the taxonomy,
not claims that each domain has one universally correct graph model.

## Use-case matrix

| Domain | Nodes | Edges | Likely model composition | Useful question |
|---|---|---|---|---|
| Software dependencies | packages, modules, tasks | requires, imports, blocks | directed; often DAG; properties | What is downstream? Is there a cycle? |
| Data pipeline | sources, transforms, outputs | feeds, produces | directed DAG + properties | What order is valid? |
| Process workflow | activities, decisions, outcomes | next, retries, branches | directed cyclic property graph | Which paths reach completion? |
| State machine | states | event-triggered transitions | directed multigraph; self-loops | Which transitions leave this state? |
| Project plan | tasks, milestones | depends_on, contributes_to | DAG + weights/properties | What can start now? |
| Decision analysis | claims, options, evidence | supports, contradicts | directed signed property graph | What evidence affects this choice? |
| Research map | papers, concepts, findings | cites, supports, extends | directed multigraph + properties | What connects two ideas? |
| Organization | people, teams, roles | reports_to, collaborates_with | mixed or layered property graph | Who owns or influences this work? |
| Resource allocation | people/tasks or jobs/candidates | eligible_for, assigned_to | bipartite weighted graph | Which matching is feasible? |
| Knowledge map | entities and concepts | typed semantic relations | directed property multigraph | What claims are explicit? |
| Taxonomy | categories and terms | broader_than, contains | rooted directed acyclic hierarchy | Does every term have a valid parent? |
| Social network | people or groups | knows, follows, communicates | directed/undirected multigraph | Which communities or bridges exist? |
| Transport | locations and services | route or connection | weighted temporal multigraph | What route is available now? |
| Event history | entities and events | participated_in, followed | temporal or bipartite property graph | What sequence occurred? |
| Argument map | claims and evidence | supports, attacks | directed signed graph | Which conclusions lack support? |
| Agent context | concepts, artifacts, decisions | depends_on, derived_from | directed property graph + confidence | What should the agent inspect next? |

## Cross-domain requirements revealed

### Stable identity

Research, project, and agent workflows revise graphs incrementally. Node and
edge identity must survive label edits, reordering, and deletion of neighboring
elements.

### Edge identity and multiplicity

Transport, research, state, event, and knowledge domains often need several
relations between the same endpoints. Independent edge IDs should therefore be
part of the general horizon even if an early validator defaults to simple
edges.

### Open vocabulary

No fixed list of `kind` values spans all domains. The core should preserve open
kinds; profiles can later offer domain vocabulary and validation.

### Bounded inspection

An agent rarely needs the entire graph after each mutation. Neighborhood,
unconnected-node, path, root/leaf, and summary views are useful across most
domains and reduce context size.

### Explicit structural policy

The same words can hide different structures. A workflow may allow retry
cycles; a build dependency graph usually must not. Model choices must be
stored explicitly rather than inferred from graph title or edge names.

### Properties without interpretation

Weights, timestamps, units, confidence, evidence locations, ownership, and
status are broadly useful. The core can store them, while a profile defines
their semantics and validators.

## Candidate trial set

Future research can use a small, diverse fixture set:

1. BookBarcode production flow — directed DAG candidate.
2. Approval workflow with revision loop — directed cyclic graph.
3. Folder hierarchy — rooted tree candidate.
4. People-to-project assignment — bipartite graph.
5. Two transport routes between the same cities — weighted multigraph.
6. Research claim with supporting and opposing evidence — signed property graph.
7. Meeting with several participants — hypergraph pressure test.

The purpose of these fixtures is to test the model contract, not to implement
every corresponding algorithm.
