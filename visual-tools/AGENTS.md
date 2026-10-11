# AGENTS.md — visual-tools

This directory contains human-facing visualization applications for artifacts
produced by deterministic tools.

Visual tools must not infer or mutate semantic claims. They consume validated
artifacts, adapt them for presentation, and keep display-specific state local
to the application.

Each application should:

* have an explicit input artifact contract;
* keep data adaptation separate from rendering;
* preserve source identifiers and directionality;
* document its development and validation commands;
* remain independently runnable from other applications.
