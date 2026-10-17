# AGENTS.md — book-editing-tools

Read `README.md` and the selected sub-tool's `SKILL.yaml` before use. These tools are read-only and deterministic. Run `manuscript_inventory` first when the input structure is unfamiliar. Keep uncertain matches visible in the result; never silently edit manuscripts or interpret thematic relationships as facts. User-authored spellings, order, and editorial decisions remain authoritative. Use a document renderer for any claim about page layout or final EPUB appearance.

When extending a sub-tool, keep its stdin JSON and Python API aligned, update its metadata and registry entry, and test normal, invalid, and boundary inputs. Prefer small extraction changes in `common.py` over one-off scripts in a chat.
