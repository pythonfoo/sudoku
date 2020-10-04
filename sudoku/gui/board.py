import asyncio
from pathlib import Path

import pygame as pg

from ..field import Field
from .events import Event
from .view import View


class Cell(View):
    def __init__(self, surface: pg.Surface, x, y, cell):
        super().__init__(surface)
        self.cell = cell
        self.x = x
        self.y = y
        self.idx = 3 * y + x
        self.font = pg.font.SysFont("Vera", 22)
        self.sfont = pg.font.SysFont("Vera", 12)

    async def draw(self, highlight=False):
        block = self.surface.get_rect()
        text_color = pg.Color("#0000ff")
        if highlight:
            pg.Color("#ff0000")
        self.surface.fill(pg.Color("#0ff00f"), block.inflate(-2, -2))
        if self.cell.value != 0:
            text = self.font.render(f"{self.cell.value}", True, text_color)
            self.surface.blit(
                text,
                text.get_rect(center=block.center),
            )
        else:
            width = self.surface.get_rect().width // 3
            for x in range(3):
                for y in range(3):
                    n = x + y * 3 + 1
                    if n not in self.cell.hopeful:
                        continue
                    mb = pg.Rect(x * width, y * width, width, width)
                    text = self.sfont.render(f"{n}", True, text_color)
                    self.surface.blit(
                        text,
                        text.get_rect(center=mb.center),
                    )


class Block(View):
    def __init__(self, surface: pg.Surface, x, y, field):
        super().__init__(surface)
        self.field = field
        self.x = x
        self.y = y
        self.idx = 3 * y + x
        self.font = pg.font.SysFont("Vera", 42)
        self.cells = []
        block = surface.get_rect()
        cell_size = (block.width - 6) // 3

        for x in range(3):
            for y in range(3):
                cellsurface = surface.subsurface(
                    pg.Rect(cell_size * x + 3, cell_size * y + 3, cell_size, cell_size)
                )
                self.cells.append(
                    Cell(
                        cellsurface,
                        x,
                        y,
                        self.field.get_cell(self.x * 3 + x, self.y * 3 + y),
                    )
                )

    async def draw(self, highlight=False):
        block = self.surface.get_rect()
        text_color = pg.Color("#0000ff")
        bg_color = pg.Color("#000000")
        if highlight:
            text_color = pg.Color("#ff0000")
            bg_color = pg.Color("#ffffff")

        self.surface.fill(bg_color, block.inflate(-6, -6))
        text = self.font.render(f"{self.idx}", True, text_color)
        self.surface.blit(
            text,
            text.get_rect(center=block.center),
        )

        for cell in self.cells:
            await cell.draw(highlight=highlight)


class Board(View):
    def __init__(self, surface: pg.Surface):
        super().__init__(surface)
        self.field = Field(
            "800000503501007000700308210680073000009005000300004805970500680063789000150040007"
        )
        self.font = pg.font.SysFont("Vera", 42)
        self.blocks = []
        self._idx = 0
        total_size = surface.get_rect()
        board_size = min(total_size.width * 2 // 3, total_size.height)
        self._board = pg.Rect(0, total_size.height - board_size, board_size, board_size)

        self.board_surface = surface.subsurface(self._board.inflate(-20, -20))

        block_size = (board_size - 20) // 3

        for x in range(3):
            for y in range(3):
                blockrect = pg.Rect(
                    block_size * x, block_size * y, block_size, block_size
                )
                blocksurface = self.board_surface.subsurface(blockrect)
                self.blocks.append(Block(blocksurface, x, y, self.field))

    async def draw(self):
        self.surface.fill(pg.Color("#ff0000"), self._board)

        self.board_surface.fill(
            pg.Color("#000000"),
        )
        # text = self.font.render(f"{board=}", True, pg.Color("#0000ff"))
        # surface.blit(
        #     text,
        #     text.get_rect(center=board.center),
        # )

        for block in self.blocks:
            mouse_pos = pg.mouse.get_pos()
            mouse_over = block.surface.get_rect(
                topleft=block.surface.get_abs_offset()
            ).collidepoint(mouse_pos)
            await block.draw(highlight=mouse_over)

    async def on_mouse_move(self, event):

        ...

    async def on_key_down(self, event):
        if event.key == pg.K_a:
            print("auto solve")

            async def auto_solve():
                # try_again = True
                # while try_again:
                print("go")
                try_again = False

                for solver in [
                    "solved",
                    "show_possibles",
                    "singles",
                    "naked_pairs",
                    "naked_triples",
                    "pointing_pairs",
                ]:
                    print(solver)

                    for change in getattr(self.field, solver)():
                        try_again = True
                        await asyncio.sleep(0.0)
                        print(f"{change.reason}")
                        self.field.apply(change)
                        if solver in ("solved", "singles"):
                            for change in self.field.show_possibles():
                                self.field.apply(change)
                    if try_again:
                        break
                if try_again:
                    pg.image.save(self.surface, f"/tmp/img{self._idx}.png")
                    self._idx += 1

            asyncio.create_task(auto_solve())
            return
        if event.key == pg.K_s:
            print("save")
            self.field.save(Path("/tmp/sudoku.savegame"))
            return
        if event.key == pg.K_l:
            print("load")
            self.field.load(Path("/tmp/sudoku.savegame"))
            return

        if event.key in (pg.K_ESCAPE, pg.K_q):
            return Event.QUIT


class GameView(View):
    ...
