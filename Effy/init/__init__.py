from __future__ import annotations
from dataclasses import dataclass
from typing import Any, cast
from Effy.types import Effect, Result, Ok, Err
from Effy.error import EffyError
from Effy.init.flags import InitFlag
from Effy._internal.registry import set_platform_adapter, get_platform_adapter
from Effy.platform import get_best_adapter

from Effy._internal.fp import pure

@dataclass(frozen=True, slots=True)
class InitContext:
    """Immutable context representing the state of initialized Effy subsystems.

    Attributes:
        flags: The set of subsystem flags that were requested during initialization.
        video_handle: The platform-specific video handle, or None if video was not initialized.
        audio_handle: The platform-specific audio handle, or None if audio was not initialized.
    """
    flags: InitFlag
    video_handle: Any = None
    audio_handle: Any = None

def init(flags: InitFlag) -> Effect[Result[InitContext, EffyError]]:
    """Initialize the requested Effy subsystems.

    Detects the best available platform adapter and initializes the video
    and audio subsystems as indicated by the provided flags.

    Args:
        flags: Bitmask of InitFlag values selecting which subsystems to start.

    Returns:
        An Effect resolving to a Result containing the InitContext or an EffyError.
    """
    def _run() -> Result[InitContext, EffyError]:
        """Thunk implementing platform subsystem detection and initialization logic."""
        # Platform detection
        adapter = get_platform_adapter() or get_best_adapter()
        set_platform_adapter(adapter)

        video_handle = None
        if flags & InitFlag.VIDEO:
            res = adapter.init_video()
            if isinstance(res, Err):
                return cast(Result[InitContext, EffyError], res)
            video_handle = res.value

        audio_handle = None
        if flags & InitFlag.AUDIO:
            res_audio = adapter.open_audio(None) # Default spec for now
            if isinstance(res_audio, Err):
                return cast(Result[InitContext, EffyError], res_audio)
            audio_handle = res_audio.value

        return Ok(InitContext(flags=flags, video_handle=video_handle, audio_handle=audio_handle))

    return Effect(_run)

def quit(ctx: InitContext) -> Effect[None]:
    """Shut down all initialized Effy subsystems and release platform resources.

    Args:
        ctx: The InitContext returned from a prior call to init.

    Returns:
        An Effect that performs the shutdown when executed.
    """
    def _run() -> None:
        """Thunk implementing platform subsystem shutdown and cleanup logic."""
        adapter = get_platform_adapter()
        if adapter:
            if ctx.video_handle:
                adapter.quit_video(ctx.video_handle)
            if ctx.audio_handle:
                adapter.close_audio(ctx.audio_handle)
        set_platform_adapter(None)
    return Effect(_run)


@pure
def was_init(ctx: InitContext, flags: InitFlag) -> bool:
    """Check if the given subsystem was initialized in the context."""
    return (ctx.flags & flags) == flags


