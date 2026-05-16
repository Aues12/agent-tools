# Skill Specification

## Purpose

A skill is a reusable workflow. It coordinates tools, agent actions, and
validation steps. A skill should describe procedure; a tool should execute a
bounded capability.

## Required Metadata

Each skill should define:

* `name`: snake_case skill name.
* `type`: `skill`.
* `purpose`: one sentence describing the workflow.
* `inputs`: required and optional inputs.
* `outputs`: expected artifacts or results.
* `steps`: ordered workflow steps.
* `tools`: tools the skill may call.
* `validation`: checks that confirm the workflow succeeded.
* `status`: `draft`, `experimental`, or `stable`.

## Step Rules

Skill steps should be concrete enough for a smaller model to follow without
reconstructing the entire workflow from first principles. When a step selects a
target, prefer semantic selectors or helper tools over raw line numbers.

## Example

```yaml
name: move_function
type: skill
purpose: Move a function from one file to another while preserving behavior.
inputs:
  required:
    - source_file
    - target_file
    - function_query
outputs:
  - modified_files
tools:
  - find_block
  - copy_paste
steps:
  - use find_block to locate the source function
  - extract the selected range
  - insert the block into the target file
  - run validation checks
validation:
  - tests pass
status: draft
```
