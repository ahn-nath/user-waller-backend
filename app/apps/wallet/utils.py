def calculate_order_amount(amount: int, limit=400) -> int:
    """Calculate order amount in cents"""

    # we are defining a limit for the amount
    if amount > limit:
        return limit * 100

    # we multiply by 100 because Stripe expects the amount in cents, and adds two zeros to the end by default
    return amount * 100
