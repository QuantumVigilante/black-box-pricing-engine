"""
my_quote.py — reimplementation of oracle.py's pricing rules.

"""

import math

_ELECTRONICS_MULTIPLIER = 1.3
_FRAGILE_SURCHARGE = 150
_BULK_THRESHOLD = 800
_BULK_DISCOUNT = 0.9
_WEIGHT_RATE = 40
_DISTANCE_RATE = 2.5
_COUPON_CODE = "WELCOME10"
_COUPON_DISCOUNT = 100


def quote(weight_kg, distance_km, category, express=False, coupon=""):
    """
    Reimplementation of oracle.quote() based on experimentally
    confirmed pricing rules. See module docstring for the model.
    """
    # 1. Billable weight: round up to the nearest 0.5 kg.
    billable_weight = math.ceil(weight_kg * 2) / 2

    # 2. Base subtotal.
    subtotal = _WEIGHT_RATE * billable_weight + _DISTANCE_RATE * distance_km

    # 3. Category adjustment.
    if category == "electronics":
        subtotal *= _ELECTRONICS_MULTIPLIER
    elif category == "fragile":
        subtotal += _FRAGILE_SURCHARGE
    # "standard", "books", "clothing", "food": no adjustment.

    # 4. Bulk discount, based on the category-adjusted subtotal.
    if subtotal > _BULK_THRESHOLD:
        subtotal *= _BULK_DISCOUNT

    # 5. Coupon: flat discount for an exact "WELCOME10" match.
    if coupon == _COUPON_CODE:
        subtotal -= _COUPON_DISCOUNT

    # `express` is intentionally unused — confirmed to have no effect.

    # 6. Round to 2 decimal places.
    return round(subtotal, 2)


def queries_used():
    """Included for interface parity with oracle.py. Not meaningful
    here since this implementation makes no external calls."""
    return 0


def reset_counter():
    """Included for interface parity with oracle.py. No-op here."""
    pass
