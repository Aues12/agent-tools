# Skills

This directory holds reusable workflows over repository tools and agent
actions. Each skill has a `SKILL.yaml` contract and a registry entry in
[`registry/skill_registry.json`](../registry/skill_registry.json).

`meta-skills/` contains workflows for creating ecosystem assets; ordinary
task workflows live here. Skills guide an agent but are not an execution
runtime. The agent reads the contract, performs the steps with the listed
tools, and checks the outputs.

- [`notes_to_semantic_graph`](notes_to_semantic_graph/README.md): create a
  source-grounded study graph from supplied notes.
