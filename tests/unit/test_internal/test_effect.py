from Effy._internal.effect import Effect

def test_effect_lazy() -> None:
    called = False
    def _run() -> int:
        nonlocal called
        called = True
        return 5
    effect = Effect(_run)
    assert not called
    assert effect.run() == 5
    assert called

def test_effect_map() -> None:
    effect = Effect(lambda: 5)
    mapped = effect.map(lambda x: x + 1)
    assert mapped.run() == 6

def test_effect_and_then() -> None:
    effect = Effect(lambda: 5)
    chained = effect.and_then(lambda x: Effect(lambda: x + 1))
    assert chained.run() == 6

def test_effect_pure() -> None:
    effect = Effect.pure(42)
    assert effect.run() == 42

def test_effect_sequence() -> None:
    effects = [Effect.pure(1), Effect.pure(2), Effect.pure(3)]
    seq = Effect.sequence(effects)
    assert seq.run() == (1, 2, 3)

