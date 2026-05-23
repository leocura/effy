import sys
import os

def get_args():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "effy"

framework = get_args()

if framework == "pygame":
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    import pygame
    pygame.init()
    pygame.display.set_mode((100, 100))
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from Effy.events.queue import EventQueue
    from Effy.events.types import QuitEvent

from runner import BenchmarkRunner

def main():
    runner = BenchmarkRunner("Pygame" if framework == "pygame" else "Effy")
    
    events_count = 5000
    
    if framework == "pygame":
        user_event = pygame.event.Event(pygame.USEREVENT)
        user_events = [pygame.event.Event(pygame.USEREVENT) for _ in range(events_count)]

        def test_push_events():
            pygame.event.clear()
            for _ in range(events_count):
                pygame.event.post(user_event)

        def test_push_many():
            pygame.event.clear()
            for e in user_events:
                pygame.event.post(e)

        def test_full_cycle():
            pygame.event.clear()
            for _ in range(events_count):
                pygame.event.post(user_event)
            pygame.event.get()
            
    else:
        effy_event = QuitEvent(timestamp=0)
        effy_events = tuple([QuitEvent(timestamp=0) for _ in range(events_count)])
        
        def test_push_events():
            q = EventQueue.empty()
            for _ in range(events_count):
                q = q.push(effy_event)
                
        def test_push_many():
            q = EventQueue.empty()
            q = q.push_many(effy_events)
            
        def test_full_cycle():
            q = EventQueue.empty().push_many(effy_events)
            while not q.is_empty():
                _, q = q.pop()

    runner.register("Push Events Seq", test_push_events, iterations=100)
    runner.register("Push Many", test_push_many, iterations=100)
    runner.register("Full Cycle", test_full_cycle, iterations=10)

    runner.dump_json()

if __name__ == "__main__":
    main()
