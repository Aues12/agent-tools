def evaluate_items(items, limit):
    total = 0
    for item in items:
        if item is None:
            continue
        if item == "stop":
            break
        try:
            value = int(item)
        except ValueError:
            value = 0
        total += value
        if total > limit:
            return total
    return total
