from __future__ import annotations

import asyncio
from pathlib import Path

import pygame as pg

from ..field import Field
from .events import Event
from .types import Surface
from .view import View

debug = {}


class Text(View):
    def __init__(self, surface: Surface, text):
        super().__init__(surface)
        self.text = text
        cell_size = min(self.surface.get_rect().width, self.surface.get_rect().height)
        self.font = pg.font.SysFont("Vera", int(cell_size * 0.9))

    async def draw(self, highlight=False):
        block = self.surface.get_rect()
        text_color = pg.Color("#000000")
        if highlight:
            text_color = pg.Color("#660000")
        # self.surface.fill(pg.Color("#ffeefe"), block.inflate(-2, -2))
        self.surface.fill(pg.Color("#00ff00"), block.inflate(-2, -2))
        text = self.font.render(f"{self.text}", True, text_color)
        self.surface.blit(
            text,
            text.get_rect(center=block.center),
        )


class Cell(View):
    def __init__(self, surface: Surface, x, y, cell):
        super().__init__(surface)
        self.cell = cell
        self.x = x
        self.y = y
        self.idx = 3 * y + x
        cell_size = min(self.surface.get_rect().width, self.surface.get_rect().height)
        self.font = pg.font.SysFont("Vera", int(cell_size * 0.6))
        self.sfont = pg.font.SysFont("Vera", int(cell_size * 0.2))

    async def draw(self, highlight=False):
        block = self.surface.get_rect()
        text_color = pg.Color("#000000")
        if highlight:
            debug["cell"] = self.cell
            text_color = pg.Color("#660000")
        self.surface.fill(pg.Color("#ffeefe"), block.inflate(-2, -2))
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
    def __init__(self, surface: Surface, x, y, field):
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
            mouse_pos = pg.mouse.get_pos()
            mouse_over = cell.surface.get_rect(
                topleft=cell.surface.get_abs_offset()
            ).collidepoint(mouse_pos)
            await cell.draw(highlight=mouse_over)


class Board(View):
    def __init__(self, surface: pg.surface.Surface):
        super().__init__(surface)
        self.field = Field(
            # "800000503501007000700308210680073000009005000300004805970500680063789000150040007"
            # "000000000904607000076804100309701080008000300050308702007502610000403208000000000"
            # "000001030231090000065003100678924300103050006000136700009360570006019843300000000"
            # "016007803090800000870001260048000300650009082039000650060900020080002936924600510"
            # "100000569492056108056109240009640801064010000218035604040500016905061402621000005"
            "100400006046091080005020000000500109090000050402009000000010900080930560500008004"
        )
        self.font = pg.font.SysFont("Vera", 42)
        self.blocks = []
        self.cells = []
        self.debugs = []
        self._idx = 0
        total_size = surface.get_rect()
        board_size = min(total_size.width * 2 // 3, total_size.height)
        board_top_space = total_size.height - board_size
        self._board = pg.Rect(0, board_top_space, board_size, board_size)
        print(total_size)
        self.board_surface = surface.subsurface(self._board.inflate(-20, -20))

        block_size = (board_size - 20) // 3
        cell_size = (block_size - 6) // 3
        for x in range(3):
            for y in range(3):
                if y == 0:
                    for i in range(3):
                        cellsurface = surface.subsurface(
                            pg.Rect(
                                block_size * x + cell_size * i + 13,
                                block_size * y + board_top_space - cell_size // 2 + 10,
                                cell_size,
                                cell_size // 2,
                            )
                        )
                        self.cells.append(
                            Text(text=f"x: {3*x+i+1}", surface=cellsurface)
                        )
                    for i in range(3):
                        rect = pg.Rect(
                            board_size - 10,
                            board_top_space + 13 + cell_size * i + block_size * x,
                            cell_size // 2,
                            cell_size,
                        )
                        print(rect)
                        cellsurface = surface.subsurface(rect)
                        self.cells.append(Text(text=f"{3*x+i+1}", surface=cellsurface))
                blockrect = pg.Rect(
                    block_size * x, block_size * y, block_size, block_size
                )
                blocksurface = self.board_surface.subsurface(blockrect)
                self.blocks.append(Block(blocksurface, x, y, self.field))

        self.debugs.append(
            Text(
                text="x: , y: ",
                surface=surface.subsurface(pg.Rect(0, 0, 200, 50)),
            )
        )

    async def draw(self):
        self.surface.fill(pg.Color("#a0a0a0"), self._board)

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
        for text in self.cells:
            await text.draw(highlight=False)
        for text in self.debugs:
            if "cell" in debug:
                text.text = (
                    f"x: {debug['cell'].position.x}, y: {debug['cell'].position.y}"
                )
                await text.draw(highlight=False)

    async def on_mouse_move(self, event): ...

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
                    "hidden_pairs",
                    "hidden_tripples",
                    "pointing_pairs",
                    "box_line_reduction",
                    "xwing",
                    "single_chains",
                ]:
                    print(solver)
                    try:
                        changes = list(getattr(self.field, solver)())
                        print(len(changes))
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
                    except Exception as e:
                        print(e)
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


class GameView(View): ...
