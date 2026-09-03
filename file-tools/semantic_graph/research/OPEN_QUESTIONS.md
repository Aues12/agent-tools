# Open questions

## Core model

* Is direction graph-wide for common models with mixed direction deferred to an
  edge-local extension?
* Which cross-cutting properties belong in policies rather than subclasses?
* Is class inheritance useful in the public API, internal implementation, or
  only the conceptual model?
* Should the serialized model use orthogonal fields such as `orientation` and
  `multiplicity`, or a compact named model plus overrides?
* What exactly makes two edges duplicates when their kinds or attributes differ?

## Identity

* Should nodes and edges expose optional symbolic keys?
* What is the canonical cross-graph address?

## Session interface

* How should dirty state recover after interruption?

## Packets, profiles, and protocols

* What minimum header distinguishes each artifact type?
* Can parameter packets reference other packets?
* How can composition stay declarative rather than become a programming
  language?
* Which layer owns protocol discovery and versioning?

## Scale

* What graph size should the in-memory prototype support comfortably?
* Which operations need bounded output for agent context?
* When should recursive algorithms be replaced with iterative implementations?

## Model boundaries

* Is bipartite behavior a model, a constraint, or both in different APIs?
* Which directed-tree convention should named hierarchy profiles adopt?
* When do temporal attributes become a true temporal graph model?
* Should hypergraphs use endpoint arrays or an incidence/bipartite projection?
* Which interoperability guarantees would justify explicit RDF support?
