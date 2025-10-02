import pygame

from .events import Event
from .types import Surface


class View:
    def __init__(self, surface: Surface):
        self.active = False
        self.surface = surface

    async def start(self):
        self.active = True

    async def end(self):
        self.active = False

    async def update(self, dt): ...

    async def draw(self, surface): ...

    async def handle_event(self, event):
        if event.type == pygame.QUIT:
            return await self.on_quit(event)
        elif event.type == pygame.MOUSEMOTION:
            return await self.on_mouse_move(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return await self.on_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return await self.on_mouse_up(event)
        elif event.type == pygame.KEYDOWN:
            return await self.on_key_down(event)
        elif event.type == pygame.KEYUP:
            return await self.on_key_up(event)

    async def on_mouse_move(self, event): ...

    async def on_mouse_click(self, event): ...

    async def on_key_press(self, event): ...

    async def on_quit(self, event): ...

    async def on_mouse_down(self, event): ...

    async def on_mouse_up(self, event): ...

    async def on_key_down(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            return Event.QUIT

    async def on_key_up(self, event): ...
