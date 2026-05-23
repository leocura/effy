from Effy._internal.fp import pipe, compose, curry, memoize, pure, identity, const, flip

def test_pipe() -> None:
    assert pipe(5, lambda x: x + 1, lambda x: x * 2) == 12

def test_compose() -> None:
    f = compose(lambda x: x * 2, lambda x: x + 1)
    assert f(5) == 12

def test_curry() -> None:
    def add(x: int, y: int) -> int:
        return x + y
    curried_add = curry(add)
    inc = curried_add(1)
    assert inc(5) == 6

def test_memoize() -> None:
    calls = 0
    def f(x: int) -> int:
        nonlocal calls
        calls += 1
        return x * 2
    mf = memoize(f)
    assert mf(5) == 10
    assert mf(5) == 10
    assert calls == 1

def test_memoize_bounds() -> None:
    calls = 0
    def f(x: int) -> int:
        nonlocal calls
        calls += 1
        return x + 1
    
    # Memoize with a maxsize of 2
    mf = memoize(f, maxsize=2)
    assert mf(1) == 2
    assert mf(2) == 3
    assert calls == 2
    
    # Hit them again, should be cached
    assert mf(1) == 2
    assert mf(2) == 3
    assert calls == 2
    
    # Add a third, should evict key 1 (since 2 was hit last, and is at the end)
    assert mf(3) == 4
    assert calls == 3
    
    # Key 1 was evicted, calling it should call the original function again
    assert mf(1) == 2
    assert calls == 4

def test_pure() -> None:
    def f(x: int) -> int: return x
    assert pure(f) == f

def test_identity() -> None:
    assert identity(5) == 5

def test_const() -> None:
    f = const(5)
    assert f(1, 2, 3) == 5

def test_flip() -> None:
    def f(a: int, b: int) -> int: return a - b
    ff = flip(f)
    assert ff(5, 10) == 5 # 10 - 5
