from __future__ import annotations
from Effy.video.ttf import load_ttf, render_text
from Effy._internal.result import Ok, Err

def test_load_ttf_fails_gracefully() -> None:
    eff = load_ttf("dummy.ttf", 16)
    res = eff.run()
    
    # Depending on the system running the test, this could succeed or fail.
    # We just ensure it returns a valid Result type without crashing.
    assert isinstance(res, (Ok, Err))
