# AGENTS.md — book-editing-tools

Read `README.md` and the selected sub-tool's `SKILL.yaml` before use. The audits and `chapter_plan` are read-only; `docx_assemble` may create a new DOCX only after a matching dry-run preview. Run `manuscript_inventory` first when the input structure is unfamiliar. Keep uncertain matches visible in the result; never silently edit manuscripts or interpret thematic relationships as facts. User-authored spellings, order, and editorial decisions remain authoritative. Use a document renderer for any claim about page layout or final EPUB appearance.

When extending a sub-tool, keep its stdin JSON and Python API aligned, update its metadata and registry entry, and test normal, invalid, and boundary inputs. Put shared extraction in `common.py`, plan types in `book_model.py`, and avoid one-off scripts in a chat.
