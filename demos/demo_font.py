import time
from Effy.init import init, quit, InitFlag
from Effy.video.window import create_window, destroy_window, WindowFlags
from Effy.render.renderer import (
    create_renderer, render_clear, render_set_draw_color,
    render_present, RendererFlags, render_text
)
from Effy.video.font import BitmapFont
from Effy.video.surface import PixelBuffer
from Effy.video.rect import Rect
from Effy.types import Color
from Effy.events import poll_event, QuitEvent
from Effy._internal.result import Ok

def create_mock_font() -> BitmapFont:
    """A programmatic 8x8 block font to serve as an atlas for the demo."""
    letters = {
        'A': ["  ###  ", " #   # ", " #   # ", " ##### ", " #   # ", " #   # ", " #   # ", "       "],
        'B': [" ####  ", " #   # ", " #   # ", " ####  ", " #   # ", " #   # ", " ####  ", "       "],
        'C': ["  #### ", " #     ", " #     ", " #     ", " #     ", " #     ", "  #### ", "       "],
        'D': [" ####  ", " #   # ", " #   # ", " #   # ", " #   # ", " #   # ", " ####  ", "       "],
        'E': [" ##### ", " #     ", " #     ", " ####  ", " #     ", " #     ", " ##### ", "       "],
        'F': [" ##### ", " #     ", " #     ", " ####  ", " #     ", " #     ", " #     ", "       "],
        'G': ["  #### ", " #     ", " #     ", " # ### ", " #   # ", " #   # ", "  #### ", "       "],
        'H': [" #   # ", " #   # ", " #   # ", " ##### ", " #   # ", " #   # ", " #   # ", "       "],
        'I': ["  ###  ", "   #   ", "   #   ", "   #   ", "   #   ", "   #   ", "  ###  ", "       "],
        'J': ["    ## ", "     # ", "     # ", "     # ", "     # ", " #   # ", "  ###  ", "       "],
        'K': [" #   # ", " #  #  ", " # #   ", " ##    ", " # #   ", " #  #  ", " #   # ", "       "],
        'L': [" #     ", " #     ", " #     ", " #     ", " #     ", " #     ", " ##### ", "       "],
        'M': [" #   # ", " ## ## ", " # # # ", " # # # ", " #   # ", " #   # ", " #   # ", "       "],
        'N': [" #   # ", " ##  # ", " # # # ", " #  ## ", " #   # ", " #   # ", " #   # ", "       "],
        'O': ["  ###  ", " #   # ", " #   # ", " #   # ", " #   # ", " #   # ", "  ###  ", "       "],
        'P': [" ####  ", " #   # ", " #   # ", " ####  ", " #     ", " #     ", " #     ", "       "],
        'Q': ["  ###  ", " #   # ", " #   # ", " #   # ", " # # # ", " #  ## ", "  ### #", "       "],
        'R': [" ####  ", " #   # ", " #   # ", " ####  ", " # #   ", " #  #  ", " #   # ", "       "],
        'S': ["  #### ", " #     ", "  ###  ", "     # ", "     # ", " #   # ", "  ###  ", "       "],
        'T': [" ##### ", "   #   ", "   #   ", "   #   ", "   #   ", "   #   ", "   #   ", "       "],
        'U': [" #   # ", " #   # ", " #   # ", " #   # ", " #   # ", " #   # ", "  ###  ", "       "],
        'V': [" #   # ", " #   # ", " #   # ", " #   # ", " #   # ", "  # #  ", "   #   ", "       "],
        'W': [" #   # ", " #   # ", " # # # ", " # # # ", " # # # ", "  # #  ", "   #   ", "       "],
        'X': [" #   # ", " #   # ", "  # #  ", "   #   ", "  # #  ", " #   # ", " #   # ", "       "],
        'Y': [" #   # ", " #   # ", "  # #  ", "   #   ", "   #   ", "   #   ", "   #   ", "       "],
        'Z': [" ##### ", "    #  ", "   #   ", "  #    ", " #     ", " #     ", " ##### ", "       "],
        '!': ["   #   ", "   #   ", "   #   ", "   #   ", "   #   ", "       ", "   #   ", "       "],
        ' ': ["       ", "       ", "       ", "       ", "       ", "       ", "       ", "       "]
    }
    
    char_w, char_h = 8, 8
    cols = 6
    rows = 5
    buf = PixelBuffer.create(cols * char_w, rows * char_h)
    
    char_map = {}
    white = Color(255, 255, 255, 255)
    
    for i, (char, lines) in enumerate(letters.items()):
        c = i % cols
        r = i // cols
        
        offset_x = c * char_w
        offset_y = r * char_h
        
        for ly, line in enumerate(lines):
            for lx, pixel in enumerate(line):
                if pixel == '#':
                    buf = buf.write_pixel(offset_x + lx, offset_y + ly, white)
                    
        char_map[char] = Rect(offset_x, offset_y, char_w, char_h)
        
    # Force materialization so it's ready for fast blitting
    _ = buf._data
    return BitmapFont(buffer=buf, glyph_width=char_w, glyph_height=char_h, char_map=char_map)

def main() -> None:
    init_res = init(InitFlag.VIDEO).run()
    if not isinstance(init_res, Ok):
        return
    init_ctx = init_res.value

    win_res = create_window("Effy Bitmap Font Demo", 100, 100, 640, 480, WindowFlags.SHOWN).run()
    if not isinstance(win_res, Ok):
        return
    window = win_res.value

    renderer_res = create_renderer(window, flags=RendererFlags.SOFTWARE).run()
    if not isinstance(renderer_res, Ok):
        return
    renderer = renderer_res.value

    # Build the font atlas texture
    font = create_mock_font()

    running = True
    while running:
        event = poll_event().run()
        while event is not None:
            if isinstance(event, QuitEvent):
                running = False
            event = poll_event().run()

        renderer = render_set_draw_color(renderer, 20, 20, 30)
        renderer = render_clear(renderer)
        
        # Render our text lines via hardware-accelerated BlitCmd pipeline!
        renderer = render_text(renderer, font, "HELLO EFFY WORLD!", 50, 50)
        renderer = render_text(renderer, font, "A PURE PYTHON ENGINE", 50, 100)
        renderer = render_text(renderer, font, "NO C EXTENSIONS ALLOWED!", 50, 150)

        renderer = render_present(renderer).run()
        time.sleep(1 / 60)

    destroy_window(window).run()
    quit(init_ctx).run()

if __name__ == "__main__":
    main()
