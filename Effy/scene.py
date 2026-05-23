from __future__ import annotations
from typing import Protocol, Sequence
from dataclasses import dataclass
from Effy.events.types import Event
from Effy.render.renderer import RenderContext

class SceneTransition:
    """Base class for scene state transitions."""
    pass

@dataclass(frozen=True, slots=True)
class Push(SceneTransition):
    """Pushes a new scene onto the stack."""
    scene: Scene

@dataclass(frozen=True, slots=True)
class Pop(SceneTransition):
    """Pops the current scene off the stack."""
    pass

@dataclass(frozen=True, slots=True)
class Replace(SceneTransition):
    """Replaces the current scene with a new one."""
    scene: Scene


class Scene(Protocol):
    """Protocol defining a pure functional scene."""
    
    def update(self, events: Sequence[Event]) -> tuple[Scene, Sequence[SceneTransition]]:
        """Process events and update scene logic.
        
        Args:
            events: A sequence of accumulated events.
            
        Returns:
            A tuple containing the newly evolved Scene, and a sequence of transitions.
        """
        ...
        
    def render(self, renderer: RenderContext) -> RenderContext:
        """Render the scene.
        
        Args:
            renderer: The active RenderContext.
            
        Returns:
            The evolved RenderContext containing new draw commands.
        """
        ...


@dataclass(frozen=True, slots=True)
class SceneManager:
    """Pure functional manager for a stack of active scenes.
    
    Attributes:
        scenes: An immutable tuple representing the current scene stack. 
                The last element is the active (top) scene.
    """
    scenes: tuple[Scene, ...] = ()

    def update(self, events: Sequence[Event]) -> SceneManager:
        """Updates the top scene and applies any yielded state transitions.
        
        Args:
            events: A sequence of accumulated events.
            
        Returns:
            A new SceneManager reflecting the updated scenes and transitions.
        """
        if not self.scenes:
            return self
            
        current_scene = self.scenes[-1]
        new_scene, transitions = current_scene.update(events)
        
        # We start by replacing the top scene with its evolved version
        new_scenes = list(self.scenes[:-1])
        new_scenes.append(new_scene)
        
        # Process requested transitions sequentially
        for transition in transitions:
            if isinstance(transition, Push):
                new_scenes.append(transition.scene)
            elif isinstance(transition, Pop):
                if new_scenes:
                    new_scenes.pop()
            elif isinstance(transition, Replace):
                if new_scenes:
                    new_scenes[-1] = transition.scene
                else:
                    new_scenes.append(transition.scene)
                    
        return SceneManager(tuple(new_scenes))

    def render(self, renderer: RenderContext) -> RenderContext:
        """Renders all scenes in the stack from bottom to top.
        
        Args:
            renderer: The active RenderContext.
            
        Returns:
            The evolved RenderContext containing commands from all scenes.
        """
        for scene in self.scenes:
            renderer = scene.render(renderer)
        return renderer
