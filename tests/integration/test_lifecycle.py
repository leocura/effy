from Effy.init import init, quit, InitFlag, InitContext
from Effy.video import create_window, destroy_window, Window, WindowFlags
from Effy.events import poll_event, QuitEvent
from Effy._internal.registry import get_platform_adapter
from Effy.platform.headless import HeadlessAdapter
from Effy.types import Ok

def test_full_lifecycle() -> None:
    # 1. Init
    res = init(InitFlag.VIDEO).run()
    assert isinstance(res, Ok)
    ctx = res.value
    assert isinstance(ctx, InitContext)
    assert ctx.flags == InitFlag.VIDEO

    adapter = get_platform_adapter()
    assert isinstance(adapter, HeadlessAdapter)

    # 2. Create Window
    win_res = create_window("Test", 0, 0, 640, 480, WindowFlags.SHOWN).run()
    assert isinstance(win_res, Ok)
    win = win_res.value
    assert isinstance(win, Window)
    assert win.title == "Test"

    # 3. Poll Event (should be empty initially)
    ev = poll_event().run()
    assert ev is None

    # 4. Inject an event into headless adapter and poll
    adapter._pending_events = adapter._pending_events + (QuitEvent(timestamp=123),)
    ev = poll_event().run()
    assert isinstance(ev, QuitEvent)
    assert ev.timestamp == 123

    # 5. Cleanup
    destroy_window(win).run()
    quit(ctx).run()

    assert get_platform_adapter() is None
