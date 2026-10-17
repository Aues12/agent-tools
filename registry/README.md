# Registry

The registry maps the tools and skills currently described by this repository.
Executor metadata is a possible future extension.

`registry/` is the canonical home for registry data in this repository.

For now these files are simple JSON documents.

## Tool Registry Shape

Tool entries keep actions and access surfaces separate:

```json
{
  "name": "semantic_cards",
  "operations": ["cards_from_file"],
  "interfaces": [
    {
      "name": "stdin_json",
      "entrypoint": "semantic_cards.py",
      "transport": "stdin_json"
    },
    {
      "name": "python_api",
      "entrypoint": "tool.py",
      "callables": ["cards_from_file", "run"]
    }
  ]
}
```

- `operations` are bounded actions a tool can perform.
- `interfaces` are access surfaces a runtime or agent can use.
