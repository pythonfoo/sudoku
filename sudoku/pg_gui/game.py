import asyncio
import time

import pygame as pg

from . import Board, View
from .events import Event


class Game:
    def __init__(self) -> None:
        pg.init()
        pg.font.init()
        pg.display.set_caption("Pyond client")
        self.screen: pg.Surface = pg.display.set_mode((1024, 768))
        self.running: bool = True
        self.stack: list[View] = []

    async def show(self, element: View) -> None:
        if self.stack:
            self.stack[-1].end()
        self.stack.append(element)
        await element.start()

    async def setup_board(self) -> None:
        await self.show(Board(self.screen))

    async def update(self, dt) -> None:
        await asyncio.gather(*[view.update(dt) for view in self.stack])

    async def draw(self) -> None:
        self.screen.fill(pg.Color("#ffeefe"))
        for view in self.stack:
            await view.draw()
        # self.screen.blit(self.bg, (0, 0))
        pg.display.flip()

    async def main_loop(self) -> None:
        now = time.monotonic()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                for view in reversed(self.stack):
                    event_response = await view.handle_event(event)
                    if event_response:
                        if event_response == Event.QUIT:
                            self.running = False
                        break
            last, now = now, time.monotonic()
            dt = now - last
            await self.update(dt)
            await self.draw()

            await asyncio.sleep(0.01)


async def amain() -> None:
    g = Game()
    await g.setup_board()
    await g.main_loop()


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
