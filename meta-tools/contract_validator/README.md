# contract_validator

Checks a single tool package's required files, YAML contract, declared
entrypoints and callables, operation/interface links, and JSON examples.
It never executes target code. Warnings and static limitations are explicit.
Run `python3 meta-tools/contract_validator/tool.py` from the repository
root with `examples/request.json` on stdin. Requires
`pip install -e '.[meta-tools]'`.
