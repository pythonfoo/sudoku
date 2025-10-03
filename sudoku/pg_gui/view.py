from typing import Optional

import pygame

from .events import Event
from .types import Surface


class View:
    def __init__(self, surface: Surface) -> None:
        self.active: bool = False
        self.surface = surface

    async def start(self) -> None:
        self.active = True

    async def end(self) -> None:
        self.active = False

    async def update(self, dt: float) -> None: ...

    async def draw(self, highlight: bool = False) -> None: ...

    async def handle_event(self, event: pygame.event.Event) -> Event | None:
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

    async def on_mouse_move(self, event: pygame.event.Event) -> Event | None: ...

    async def on_mouse_click(self, event: pygame.event.Event) -> Event | None: ...

    async def on_key_press(self, event: pygame.event.Event) -> Event | None: ...

    async def on_quit(self, event: pygame.event.Event) -> Event | None: ...

    async def on_mouse_down(self, event: pygame.event.Event) -> Event | None: ...

    async def on_mouse_up(self, event: pygame.event.Event) -> Event | None: ...

    async def on_key_down(self, event: pygame.event.Event) -> Event | None:
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            return Event.QUIT

    async def on_key_up(self, event: pygame.event.Event) -> Event | None: ...
