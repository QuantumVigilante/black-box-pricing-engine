from my_quote import quote

tests = [
    ((2, 100, "standard"), 330.0),
    ((2, 100, "electronics"), 429.0),
    ((2, 100, "fragile"), 480.0),
    ((10, 120, "standard"), 700.0),
    ((10, 120, "fragile"), 765.0),
    ((10, 120, "electronics"), 819.0),
    ((2, 100, "standard", False, "WELCOME10"), 230.0),
    ((0.1, 1, "standard", False, "WELCOME10"), -77.5),
]

for args, expected in tests:
    actual = quote(*args)

    if actual == expected:
        print("PASS:", args, "->", actual)
    else:
        print("FAIL:", args, "expected", expected, "got", actual)