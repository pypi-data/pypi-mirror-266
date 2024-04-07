def then(a: str, b: str):
    return a+b
def one_or_more(a: str, unit: bool):
    return f"{a}+" if unit else f"({a})+"
def times(a: str, n: int, unit: bool):
    return 