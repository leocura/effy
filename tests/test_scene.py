import pytest
from Effy.scene import SceneManager, Scene, SceneTransition, Push, Pop, Replace
from Effy.render.renderer import RenderContext

class MockScene(Scene):
    def __init__(self, id: int, transitions: list[SceneTransition] = []):
        self.id = id
        self.transitions = transitions
        
    def update(self, events):
        return self, self.transitions
        
    def render(self, renderer):
        return renderer

def test_scene_manager_push():
    s1 = MockScene(1, [Push(MockScene(2))])
    mgr = SceneManager((s1,))
    
    mgr2 = mgr.update([])
    assert len(mgr2.scenes) == 2
    assert mgr2.scenes[0].id == 1
    assert mgr2.scenes[1].id == 2

def test_scene_manager_pop():
    s1 = MockScene(1)
    s2 = MockScene(2, [Pop()])
    mgr = SceneManager((s1, s2))
    
    mgr2 = mgr.update([])
    assert len(mgr2.scenes) == 1
    assert mgr2.scenes[0].id == 1

def test_scene_manager_replace():
    s1 = MockScene(1, [Replace(MockScene(3))])
    mgr = SceneManager((s1,))
    
    mgr2 = mgr.update([])
    assert len(mgr2.scenes) == 1
    assert mgr2.scenes[0].id == 3
