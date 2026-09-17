"""
verify.py — verifies my_quote.py against the real oracle.py.

Uses oracle.quote() as the reference implementation and compares it
against my_quote.quote() across a broad set of valid inputs, including
boundary values, all categories, express flag, coupon variants, and
combinations of all of the above.

oracle.py is used only through its public quote() function. It is not
modified, inspected, or reverse engineered by this script.
"""

from itertools import product

from oracle import quote as oracle_quote
from my_quote import quote as my_quote

CATEGORIES = ["standard", "electronics", "fragile", "books", "clothing", "food"]
EXPRESS_VALUES = [False, True]
COUPONS = [
    "",
    "WELCOME10",       # exact match
    "welcome10",       # wrong case
    "Welcome10",       # wrong case
    "WELCOME10 ",      # trailing whitespace
    " WELCOME10",      # leading whitespace
    "BOGUSCODE",       # unrelated invalid code
]

# Weight values: min/max of the documented range, values around the
# 0.5 kg rounding boundaries, and a few decimals for rounding checks.
WEIGHTS = [
    0.1, 100.0,                # min / max
    0.5, 0.6, 1.0, 1.1,        # 0.5 kg boundary values
    13.4, 13.5, 13.6, 14.0,    # near the weight that used to look like a threshold
    2.0, 7.3, 33.33,           # general decimal values
]

# Distance values: min/max of the documented range, values around the
# $800 subtotal threshold found during investigation, and decimals.
DISTANCES = [
    1.0, 5000.0,               # min / max
    288.0, 288.1, 289.0,       # around the $800 subtotal threshold (at weight=2)
    100.0, 120.0, 333.0,       # general values used during investigation
    137.7,                     # decimal value for rounding checks
]


def build_test_cases():
    """Combine boundary-focused values with full category/express/coupon
    combinations, without doing a full (huge) cartesian product of
    every weight against every distance."""
    cases = []

    # 1. Full cartesian product of category x express x coupon at a
    #    fixed, simple (weight, distance) point -> checks every
    #    combination of the "flag" style parameters.
    for cat, exp, cp in product(CATEGORIES, EXPRESS_VALUES, COUPONS):
        cases.append((2.0, 100.0, cat, exp, cp))

    # 2. Every weight value paired with a fixed mid-range distance,
    #    across all categories, to hit weight-rounding edge cases.
    for w in WEIGHTS:
        for cat in CATEGORIES:
            cases.append((w, 100.0, cat, False, ""))
            cases.append((w, 100.0, cat, False, "WELCOME10"))

    # 3. Every distance value paired with a fixed light weight,
    #    across all categories, to hit the $800 threshold and the
    #    min/max distance range.
    for d in DISTANCES:
        for cat in CATEGORIES:
            cases.append((2.0, d, cat, False, ""))
            cases.append((2.0, d, cat, True, "WELCOME10"))

    # 4. Boundary weight/distance combined with heavier weight, to
    #    make sure the $800 threshold is exercised on both sides
    #    when combined with category adjustments.
    for w in [10.0, 13.5, 14.0, 20.0]:
        for d in [1.0, 100.0, 120.0, 289.0, 5000.0]:
            for cat in CATEGORIES:
                cases.append((w, d, cat, False, ""))
                cases.append((w, d, cat, True, "WELCOME10"))

    # 5. Extreme min/max combined (both directions) across categories
    #    and coupon states.
    for w in [0.1, 100.0]:
        for d in [1.0, 5000.0]:
            for cat in CATEGORIES:
                for exp in EXPRESS_VALUES:
                    for cp in ["", "WELCOME10"]:
                        cases.append((w, d, cat, exp, cp))

    # De-duplicate while preserving order (many combinations above
    # legitimately overlap).
    seen = set()
    unique_cases = []
    for c in cases:
        if c not in seen:
            seen.add(c)
            unique_cases.append(c)
    return unique_cases


def main():
    cases = build_test_cases()
    total = len(cases)
    mismatches = []

    for args in cases:
        weight, distance, category, express, coupon = args
        oracle_result = oracle_quote(weight, distance, category, express, coupon)
        my_result = my_quote(weight, distance, category, express, coupon)
        if oracle_result != my_result:
            mismatches.append((args, oracle_result, my_result))

    print(f"Total tests:      {total}")
    print(f"Matching tests:   {total - len(mismatches)}")
    print(f"Mismatching tests:{len(mismatches)}")
    print()

    if mismatches:
        print("=== MISMATCH DETAILS ===")
        for args, oracle_result, my_result in mismatches:
            weight, distance, category, express, coupon = args
            print(
                f"quote(weight_kg={weight}, distance_km={distance}, "
                f"category={category!r}, express={express}, coupon={coupon!r})"
            )
            print(f"  oracle result   : {oracle_result}")
            print(f"  my_quote result : {my_result}")
            print()
    else:
        print("All tests matched. No mismatches found.")


if __name__ == "__main__":
    main()
