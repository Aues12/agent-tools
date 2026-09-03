# Open questions

## Core model

* Is the base `Graph` directed, undirected, mixed, or neutral?
* Is direction graph-wide or edge-local?
* Should self-loops and parallel edges be accepted by default?
* Which cross-cutting properties belong in policies rather than subclasses?
* Is class inheritance useful in the public API, internal implementation, or
  only the conceptual model?

## Identity

* Are graph-local integer IDs assigned only by the tool or optionally accepted
  from callers?
* Should nodes and edges expose optional symbolic keys?
* What is the canonical cross-graph address?
* Are counters stored directly or derived from an append-only identity record?

## Session interface

* Shell-like commands or newline-delimited JSON?
* Structured JSON responses by default or compact text?
* Auto-save after every valid mutation or explicit save/checkpoint?
* How should dirty state recover after interruption?
* Is a single active graph enough for the first session prototype?

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
