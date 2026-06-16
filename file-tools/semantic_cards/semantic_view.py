"""Compact semantic views over existing semantic_cards output."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any


NO_SUMMARY = "No summary available."


def build_card_index(cards: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Return card_id -> card mapping."""
    result: dict[str, dict[str, Any]] = {}
    for card in _card_list(cards):
        card_id = card.get("id")
        if isinstance(card_id, str):
            result[card_id] = dict(card)
    return result


def build_children_index(cards: Mapping[str, Any]) -> dict[str | None, list[dict[str, Any]]]:
    """Return parent_id -> child card list mapping."""
    children: dict[str | None, list[dict[str, Any]]] = defaultdict(list)
    for card in _card_list(cards):
        parent_id = card.get("parent_id")
        key = parent_id if isinstance(parent_id, str) else None
        children[key].append(dict(card))
    return dict(children)


def build_relation_index(cards: Mapping[str, Any]) -> dict[str, dict[str, dict[str, list[str]]]]:
    """Group relations by source and target card ids."""
    index: dict[str, dict[str, dict[str, list[str]]]] = {
        "outgoing": defaultdict(lambda: defaultdict(list)),
        "incoming": defaultdict(lambda: defaultdict(list)),
    }

    for relation in _relation_list(cards):
        kind = _relation_kind(relation)
        source_id = relation.get("source_id")
        target = _relation_target(relation)
        if isinstance(source_id, str) and target:
            index["outgoing"][source_id][kind].append(target)
        target_id = relation.get("target_id")
        if isinstance(target_id, str) and isinstance(source_id, str):
            index["incoming"][target_id][kind].append(source_id)

    return {
        direction: {
            card_id: {
                kind: sorted(set(targets))
                for kind, targets in kinds.items()
            }
            for card_id, kinds in card_relations.items()
        }
        for direction, card_relations in index.items()
    }


def summary_view(cards: Mapping[str, Any], max_relations: int = 10) -> dict[str, Any]:
    """Return a compact overview of a semantic_cards result."""
    _validate_cards(cards)
    if not isinstance(max_relations, int):
        raise TypeError("max_relations must be an integer")
    if max_relations < 0:
        raise ValueError("max_relations must be >= 0")

    card_items = _card_list(cards)
    counts = Counter(_card_kind(card) for card in card_items)
    top_level = [
        _display_card(card)
        for card in card_items
        if card.get("parent_id") in {None, _root_id(cards)}
        and _card_kind(card) != "module"
    ]
    relations = [
        _display_relation(relation)
        for relation in _relation_list(cards)
        if relation.get("kind") != "contains"
    ][:max_relations]

    return {
        "type": "semantic_summary_view",
        "source": _source_name(cards),
        "counts": dict(sorted(counts.items())),
        "top_level": top_level,
        "relations": relations,
    }


def tree_view(
    cards: Mapping[str, Any],
    max_depth: int = 3,
    include_statements: bool = False,
) -> dict[str, Any]:
    """Return a compact text containment tree."""
    _validate_cards(cards)
    if not isinstance(max_depth, int):
        raise TypeError("max_depth must be an integer")
    if max_depth < 0:
        raise ValueError("max_depth must be >= 0")

    card_index = build_card_index(cards)
    children_index = build_children_index(cards)
    roots = _root_cards(cards, card_index, children_index)
    lines: list[str] = []

    for root_index, root in enumerate(roots):
        _render_tree_card(
            card=root,
            children_index=children_index,
            lines=lines,
            prefix="",
            is_last=root_index == len(roots) - 1,
            depth=0,
            max_depth=max_depth,
            include_statements=include_statements,
            is_root=True,
        )

    return {
        "type": "semantic_tree_view",
        "format": "text",
        "tree": "\n".join(lines),
    }


def card_view(cards: Mapping[str, Any], card_id: str) -> dict[str, Any]:
    """Return a compact view of one semantic card."""
    _validate_cards(cards)
    if not isinstance(card_id, str) or not card_id:
        raise ValueError("card_view requires card_id")

    card_index = build_card_index(cards)
    card = card_index.get(card_id)
    if card is None:
        raise ValueError(f"card not found: {card_id}")

    relation_index = build_relation_index(cards)
    return {
        "type": "semantic_card_view",
        "card_id": card_id,
        "kind": _card_kind(card),
        "title": _card_title(card),
        "depth": card.get("depth"),
        "level": card.get("level"),
        "location": _location(card),
        "parent_id": card.get("parent_id"),
        "children": list(card.get("children", [])),
        "relations": {
            "outgoing": relation_index["outgoing"].get(card_id, {}),
            "incoming": relation_index["incoming"].get(card_id, {}),
        },
        "summary": _summary(card),
    }


def _validate_cards(cards: Mapping[str, Any]) -> None:
    """Ensure the value looks like a semantic_cards result."""
    if not isinstance(cards, Mapping):
        raise TypeError("cards must be a dictionary")
    if "cards" not in cards:
        raise ValueError("semantic view operations require cards")
    if not isinstance(cards.get("cards"), list):
        raise TypeError("cards.cards must be a list")
    if "relations" in cards and not isinstance(cards.get("relations"), list):
        raise TypeError("cards.relations must be a list")


def _card_list(cards: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return normalized card dictionaries from the payload."""
    items = cards.get("cards", [])
    return [dict(item) for item in items if isinstance(item, Mapping)]


def _relation_list(cards: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return normalized relation dictionaries from the payload."""
    items = cards.get("relations", [])
    return [dict(item) for item in items if isinstance(item, Mapping)]


def _root_id(cards: Mapping[str, Any]) -> str | None:
    """Return the first root card id when available."""
    root_ids = cards.get("root_ids")
    if isinstance(root_ids, list) and root_ids and isinstance(root_ids[0], str):
        return root_ids[0]
    return None


def _root_cards(
    cards: Mapping[str, Any],
    card_index: Mapping[str, dict[str, Any]],
    children_index: Mapping[str | None, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Resolve root cards from root_ids or top-level children."""
    root_id = _root_id(cards)
    if root_id and root_id in card_index:
        return [card_index[root_id]]
    return children_index.get(None, [])


def _render_tree_card(
    *,
    card: Mapping[str, Any],
    children_index: Mapping[str | None, list[dict[str, Any]]],
    lines: list[str],
    prefix: str,
    is_last: bool,
    depth: int,
    max_depth: int,
    include_statements: bool,
    is_root: bool = False,
) -> None:
    """Append one card and its visible children to text tree lines."""
    if not include_statements and _card_kind(card) == "statement":
        return

    connector = "" if is_root else ("`- " if is_last else "+- ")
    lines.append(f"{prefix}{connector}{_tree_label(card)}")
    if depth >= max_depth:
        return

    card_id = card.get("id")
    children = children_index.get(card_id, []) if isinstance(card_id, str) else []
    visible_children = [
        child
        for child in children
        if include_statements or _card_kind(child) != "statement"
    ]
    child_prefix = prefix if is_root else prefix + ("   " if is_last else "|  ")
    for index, child in enumerate(visible_children):
        _render_tree_card(
            card=child,
            children_index=children_index,
            lines=lines,
            prefix=child_prefix,
            is_last=index == len(visible_children) - 1,
            depth=depth + 1,
            max_depth=max_depth,
            include_statements=include_statements,
        )


def _display_card(card: Mapping[str, Any]) -> str:
    """Format one card as kind:title."""
    return f"{_card_kind(card)}:{_card_title(card)}"


def _tree_label(card: Mapping[str, Any]) -> str:
    """Format one card label for the tree view."""
    return f"{_card_kind(card)}: {_card_title(card)}"


def _display_relation(relation: Mapping[str, Any]) -> str:
    """Format one relation for the summary view."""
    source = relation.get("source_id")
    target = _relation_target(relation)
    if source and target:
        return f"{source} -> {target}"
    return str(relation.get("kind", "relation"))


def _relation_target(relation: Mapping[str, Any]) -> str | None:
    """Return the target id or external target name."""
    target_id = relation.get("target_id")
    if isinstance(target_id, str):
        return target_id
    target = relation.get("target")
    return target if isinstance(target, str) else None


def _relation_kind(relation: Mapping[str, Any]) -> str:
    """Return a relation kind with a safe fallback."""
    kind = relation.get("kind")
    return kind if isinstance(kind, str) and kind else "related"


def _card_kind(card: Mapping[str, Any]) -> str:
    """Return a card kind with a safe fallback."""
    kind = card.get("kind")
    return kind if isinstance(kind, str) and kind else "card"


def _card_title(card: Mapping[str, Any]) -> str:
    """Return a readable card title."""
    title = card.get("title")
    if isinstance(title, str) and title:
        return title
    card_id = card.get("id")
    return card_id if isinstance(card_id, str) else "untitled"


def _source_name(cards: Mapping[str, Any]) -> str | None:
    """Return the source file name or root id for display."""
    path = cards.get("path")
    if isinstance(path, str) and path:
        return Path(path).name
    roots = cards.get("root_ids")
    if isinstance(roots, list) and roots and isinstance(roots[0], str):
        return roots[0]
    return None


def _location(card: Mapping[str, Any]) -> str | None:
    """Return a compact line range from card trace data."""
    trace = card.get("trace")
    if not isinstance(trace, Mapping):
        return None
    line = trace.get("line")
    end_line = trace.get("end_line")
    if isinstance(line, int) and isinstance(end_line, int):
        return f"L{line}" if line == end_line else f"L{line}-L{end_line}"
    if isinstance(line, int):
        return f"L{line}"
    return None


def _summary(card: Mapping[str, Any]) -> str:
    """Return the best available card summary text."""
    detail = card.get("detail")
    if isinstance(detail, Mapping):
        docstring = detail.get("docstring")
        if isinstance(docstring, str) and docstring.strip():
            return docstring.strip()
        summary = detail.get("summary")
        if isinstance(summary, str) and summary.strip():
            return summary.strip()
    return NO_SUMMARY
