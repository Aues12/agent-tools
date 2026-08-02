# semantic_cfg playground output

Source:

```text
agent-playground/semantic_cfg/branch_loop_try_example.py
```

Command:

```sh
printf '%s' '{"operation":"build_cfg_from_file","params":{"path":"agent-playground/semantic_cfg/branch_loop_try_example.py"}}' | python3 file-tools/semantic_cfg/semantic_cfg.py
```

Result stats:

```text
functions: 1
nodes: 20
edges: 24
warnings: 1
```

Function:

```text
branch_loop_try_example.evaluate_items
```

Notable edge kinds:

```text
next
loop_body
loop_exit
loop_back
branch_true
branch_false
continue
break
exception
return
```

Warning:

```text
PartialAnalysis at line 8: try is modeled with normal and handler paths only.
```

Compact flow:

```text
entry
  -> assign total
  -> for loop
      -> if item is None
          true  -> continue -> loop
          false -> if item == "stop"
              true  -> break -> loop exit
              false -> try
                  normal    -> value = int(item)
                  exception -> value = 0
                  join      -> total += value
                      -> if total > limit
                          true  -> return total -> exit
                          false -> loop back
  -> final return total -> exit
```
