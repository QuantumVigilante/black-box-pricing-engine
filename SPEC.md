# SPEC :- oracle.py Pricing Rules

All rules below were determined purely by calling `oracle.quote()` with
different inputs and observing the outputs. `oracle.py`'s implementation
was never opened, read, decompiled, or otherwise inspected.

## Rule 1 :- Billable weight rounds up to the nearest 0.5 kg

The raw `weight_kg` is not billed directly. It is rounded **up** to the
nearest 0.5 kg increment before anything else happens.

**Example:** every weight from 0.6 to 1.0 kg produced the same price
(290.0), and every weight from 1.1 to 1.5 kg produced the same price
(310.0):

```
quote(0.6, 100, "standard")  -> 290.0
quote(1.0, 100, "standard")  -> 290.0
quote(1.1, 100, "standard")  -> 310.0
quote(1.5, 100, "standard")  -> 310.0
```

## Rule 2 :- Base subtotal formula

Before any category, discount, or coupon logic, the base subtotal is:

```
subtotal = 40 * billable_weight + 2.5 * distance_km
```

Distance is used as given — no rounding of distance was detected.

**Example:**

```
quote(2.0, 100, "standard") -> 330.0
# 40 * 2 + 2.5 * 100 = 80 + 250 = 330
```

## Rule 3 :- Category adjustment

- **electronics**: multiplies the subtotal by **1.3**
- **fragile**: adds a flat **150** to the subtotal
- **standard, books, clothing, food**: no adjustment — all four behave
  identically

**Examples:**

```
quote(2.0, 100, "electronics") -> 429.0   # 330 * 1.3 = 429
quote(2.0, 100, "fragile")     -> 480.0   # 330 + 150 = 480
quote(7.0, 333, "standard")    -> 1001.25
quote(7.0, 333, "books")       -> 1001.25
quote(7.0, 333, "clothing")    -> 1001.25
quote(7.0, 333, "food")        -> 1001.25
```

## Rule 4 :- Bulk discount at $800

If the subtotal **after** the category adjustment is **strictly greater
than 800**, a 10% discount is applied (multiply by 0.9). At exactly 800
or below, no discount applies. The threshold is checked on the
post-category subtotal, not on the base (pre-category) subtotal.


```
quote(2.0, 288.0, "standard") -> 800.0    # subtotal = 800 exactly, no discount
quote(2.0, 288.1, "standard") -> 720.23   # subtotal = 800.25, discount applied
```

```
quote(10.0, 120, "standard")   -> 700.0    # base subtotal 700, no discount
quote(10.0, 120, "fragile")    -> 765.0    # (700 + 150) * 0.9 = 765
quote(10.0, 120, "electronics")-> 819.0    # (700 * 1.3) * 0.9 = 819
```

## Rule 5 :- Coupon "WELCOME10"

An exact, case-sensitive match of the coupon string `"WELCOME10"`
subtracts a flat **100** from the price, applied **after** the category
adjustment and the bulk discount. Any other string — including
different casing or surrounding whitespace — has no effect.

**Examples:**

```
quote(2.0, 100, "standard", False, "WELCOME10")  -> 230.0   # 330 - 100
quote(20.0, 100, "fragile", False, "WELCOME10")  -> 980.0   # 1080 - 100 (discount already applied)
quote(2.0, 100, "standard", False, "welcome10")  -> 330.0   # no effect
quote(2.0, 100, "standard", False, " WELCOME10") -> 330.0   # no effect
```

No floor at zero was observed - a small order with the coupon can go
negative:

```
quote(0.1, 1, "standard", False, "WELCOME10") -> -77.5
```

## Rule 6 :- `express` has no effect

`express=True` produced the exact same price as `express=False` in
every test: all six categories, small and large orders, with and
without the coupon.

**Example:**

```
quote(20.0, 100, "standard", False, "") -> 945.0
quote(20.0, 100, "standard", True, "")  -> 945.0
```

## Rule 7 :- Rounding

The final price is rounded to 2 decimal places, matching the
docstring in `oracle.py`.

---

## Rejected hypotheses

- **"Bulk discount triggers when weight ≥ 14 kg OR distance ≥ 289 km"**:-
  rejected. `quote(14.0, 1, "standard")` returned 562.5, the
  *non-discounted* price, even though weight (14 kg) met the
  originally-suspected weight threshold. The real trigger is a single
  unified rule: the category-adjusted subtotal exceeding $800 — weight
  and distance only matter insofar as they drive that subtotal up.

- **"WELCOME10 is a 10% discount"** :- rejected, despite the "10" in the
  name. It is a flat -$100 regardless of order size: it removed exactly
  100 from a $330 order and exactly 100 from a $945 order.

- **"fragile is a percentage multiplier like electronics"** :- rejected.
  The ratio of fragile price to standard price was not constant across
  different order sizes (e.g. 480/330 ≠ 1080/945), which a multiplier
  would require. A flat +$150 addition fit every observed case exactly.

- **"express affects price under some untested condition"** :- rejected
  after testing it across all six categories, at both small and large
  order sizes, and combined with the coupon. It never changed the
  result.

---

