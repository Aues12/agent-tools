# create_tool

This meta-skill turns a capability idea into a concrete tool package.

It should be used when the repository needs a new deterministic capability, not
when an existing tool can be composed into the requested behavior.

Generated tool metadata should follow the current tool contract:

- `interfaces` describe access surfaces such as `stdin_json` and `python_api`.
- `operations` describe bounded actions with params, returns, and `available_via`.
- `registry/tool_registry.json` should use the same separation.
