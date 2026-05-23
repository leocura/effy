from Effy._internal.result import Ok, Err
from hypothesis import given, strategies as st

def test_ok_map() -> None:
    ok = Ok(5)
    result = ok.map(lambda x: x + 1)
    assert result == Ok(6)

def test_err_map() -> None:
    err: Err[str] = Err("error")
    result = err.map(lambda x: x + 1)
    assert result == Err("error")

def test_ok_and_then() -> None:
    ok = Ok(5)
    result = ok.and_then(lambda x: Ok(x + 1))
    assert result == Ok(6)

def test_err_and_then() -> None:
    err: Err[str] = Err("error")
    result = err.and_then(lambda x: Ok(x + 1))
    assert result == Err("error")

@given(st.integers())
def test_ok_map_property(x: int) -> None:
    ok = Ok(x)
    assert ok.map(lambda v: v + 1) == Ok(x + 1)
