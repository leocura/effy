from __future__ import annotations
import time
from Effy.filesystem.asset_manager import AssetManager, load_asset_async
from Effy._internal.result import Ok, Err

def test_asset_manager_lru() -> None:
    am: AssetManager[str, str] = AssetManager(max_size=2)
    
    # Insert 3 items into size 2 cache
    am = am.insert("a", "Asset A")
    am = am.insert("b", "Asset B")
    am = am.insert("c", "Asset C")
    
    # 'a' should be evicted
    am, val_a = am.get("a")
    assert val_a is None
    
    am, val_c = am.get("c")
    assert val_c == "Asset C"
    
    am, val_b = am.get("b")
    assert val_b == "Asset B"
    
    # getting 'b' makes it the most recently used
    am = am.insert("d", "Asset D")
    
    # now 'c' should be evicted instead of 'b'
    am, val_c2 = am.get("c")
    assert val_c2 is None
    
    am, val_b2 = am.get("b")
    assert val_b2 == "Asset B"
    
def test_load_asset_async() -> None:
    def slow_load() -> Ok[str]:
        time.sleep(0.01)
        return Ok("Loaded")
        
    eff = load_asset_async(slow_load)
    
    # Run the effect to block and get the result
    res = eff.run()
    assert isinstance(res, Ok)
    assert res.value == "Loaded"
