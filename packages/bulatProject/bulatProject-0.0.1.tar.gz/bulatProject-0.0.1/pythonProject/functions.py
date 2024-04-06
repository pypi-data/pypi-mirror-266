def hello(name: str):
    print(f"Hello {name}!")


def sum_on_range(l: int, r: int) -> int:
    assert l <= r
    return (r + l) * (r - l + 1) // 2
