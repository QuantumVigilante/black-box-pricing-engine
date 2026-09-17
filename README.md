# Black-Box Pricing Engine — Reverse Engineering

This repository reverse-engineers the pricing rules of `oracle.py`, a
compiled "black box" shipping quote engine, purely through black-box
experimentation against its public `quote()` function. The
implementation of `oracle.py` was never opened, read, decompiled, or
otherwise inspected — every rule below was inferred from observed
input/output behavior.

## Files

| File | Purpose |
|---|---|
| `oracle.py` | The original black-box engine, provided as-is |
| `my_quote.py` | Reimplementation of the pricing logic, with the same `quote()` signature, that does **not** import or call `oracle.py` |
| `SPEC.md` | Full documentation of every discovered pricing rule, with real examples, rejected hypotheses, and the investigation process summary |
| `verify.py` | Compares `my_quote.py` against the real `oracle.py` across 648 test cases |
| `check.py` | A lightweight regression check using hardcoded known-good oracle outputs — has no dependency on `oracle.py`, so it runs even in environments where importing `oracle.py` fails |

## Pricing rules (summary)

See `SPEC.md` for the full write-up with examples and evidence. In short:

1. **Weight** is rounded up to the nearest 0.5 kg before billing.
2. **Base subtotal** = `40 × billable_weight + 2.5 × distance_km`.
3. **Category adjustment**:
   - `electronics` → subtotal × 1.3
   - `fragile` → subtotal + 150
   - `standard`, `books`, `clothing`, `food` → no adjustment
4. **Bulk discount**: if the category-adjusted subtotal is **strictly
   greater than 800**, apply a 10% discount (× 0.9). Exactly 800 gets
   no discount.
5. **Coupon**: an exact, case-sensitive match of `"WELCOME10"`
   subtracts a flat 100, applied **after** the bulk discount. No other
   string has any effect, and there is no floor at zero.
6. **`express`** has no effect on price under any tested condition.
7. The final result is rounded to 2 decimal places.

## Verification

`my_quote.py` was checked against the real `oracle.py` using
`verify.py`, covering weight/distance extremes, the 0.5 kg rounding
boundaries, the $800 threshold boundary, all six categories, both
`express` values, and several coupon variants:

```
Total tests:      648
Matching tests:   648
Mismatching tests:0

All tests matched. No mismatches found.
```

`check.py` provides a smaller, oracle-independent sanity check against
8 known-good outputs:

```
PASS: (2, 100, 'standard') -> 330.0
PASS: (2, 100, 'electronics') -> 429.0
PASS: (2, 100, 'fragile') -> 480.0
PASS: (10, 120, 'standard') -> 700.0
PASS: (10, 120, 'fragile') -> 765.0
PASS: (10, 120, 'electronics') -> 819.0
PASS: (2, 100, 'standard', False, 'WELCOME10') -> 230.0
PASS: (0.1, 1, 'standard', False, 'WELCOME10') -> -77.5
```

## Running it

```bash
# Compare my_quote.py against the real oracle (requires oracle.py to import successfully)
python3 verify.py

# Run the oracle-independent regression check
python3 check.py
```
