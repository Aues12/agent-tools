def calculate_total(price, quantity, tax_rate):
    subtotal = price * quantity
    tax = subtotal * tax_rate
    total = subtotal + tax
    return total
