def apply_discount(price, rate):
    discount = price * rate
    return price - discount


def calculate_total(price, quantity, tax_rate):
    subtotal = price * quantity
    if subtotal > 100:
        subtotal = apply_discount(subtotal, 0.1)
    tax = subtotal * tax_rate
    return subtotal + tax


def main():
    return calculate_total(25, 5, 0.2)
