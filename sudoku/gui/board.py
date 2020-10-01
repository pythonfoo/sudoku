from .view import View
from ..field import Field
import pygame as pg


class Cell(View):
    def __init__(self, x, y, cell):
        super().__init__()
        self.cell = cell
        self.x = x
        self.y = y
        self.idx = 3 * y + x
        self.font = pg.font.SysFont("Vera", 22)
        self.sfont = pg.font.SysFont("Vera", 12)

    async def draw(self, surface, highlight=False):
        block = surface.get_rect()
        text_color = pg.Color("#0000ff")
        if highlight:
            pg.Color("#ff0000")
        surface.fill(pg.Color("#0ff00f"), block.inflate(-2, -2))
        if self.cell.value != 0:
            text = self.font.render(f"{self.cell.value}", True, text_color)
            surface.blit(
                text,
                text.get_rect(center=block.center),
            )
        else:
            width = surface.get_rect().width // 3
            for x in range(3):
                for y in range(3):
                    n = x + y * 3 + 1
                    if n not in self.cell.hopeful:
                        continue
                    mb = pg.Rect(x * width, y * width, width, width)
                    text = self.sfont.render(f"{n}", True, text_color)
                    surface.blit(
                        text,
                        text.get_rect(center=mb.center),
                    )


class Block(View):
    def __init__(self, x, y, field):
        super().__init__()
        self.field = field
        self.x = x
        self.y = y
        self.idx = 3 * y + x
        self.font = pg.font.SysFont("Vera", 42)
        self.cells = []
        for x in range(3):
            for y in range(3):
                self.cells.append(
                    Cell(x, y, self.field.get_cell(self.x * 3 + x, self.y * 3 + y))
                )

    async def draw(self, surface, highlight=False):
        block = surface.get_rect()
        text_color = pg.Color("#0000ff")
        bg_color = pg.Color("#000000")
        if highlight:
            text_color = pg.Color("#ff0000")
            bg_color = pg.Color("#ffffff")

        surface.fill(bg_color, block.inflate(-6, -6))
        text = self.font.render(f"{self.idx}", True, text_color)
        surface.blit(
            text,
            text.get_rect(center=block.center),
        )
        cell_size = (block.width - 6) // 3

        for cell in self.cells:
            x, y = cell.x, cell.y
            cellsurface = surface.subsurface(
                pg.Rect(cell_size * x + 3, cell_size * y + 3, cell_size, cell_size)
            )
            await cell.draw(cellsurface, highlight=highlight)


class Board(View):
    def __init__(
        self,
    ):
        super().__init__()
        self.field = Field(
            "800000503501007000700308210680073000009005000300004805970500680063789000150040007"
        )
        self.font = pg.font.SysFont("Vera", 42)
        self.blocks = []
        for x in range(3):
            for y in range(3):
                self.blocks.append(Block(x, y, self.field))

    async def draw(self, surface):
        total_size = surface.get_rect()
        board_size = min(total_size.width * 2 // 3, total_size.height)
        board = pg.Rect(0, total_size.height - board_size, board_size, board_size)
        surface.fill(pg.Color("#ff0000"), board)

        board_surface = surface.subsurface(board.inflate(-20, -20))
        board_surface.fill(
            pg.Color("#000000"),
        )
        # text = self.font.render(f"{board=}", True, pg.Color("#0000ff"))
        # surface.blit(
        #     text,
        #     text.get_rect(center=board.center),
        # )
        block_size = (board_size - 20) // 3

        for block in self.blocks:
            x, y = block.x, block.y
            blockrect = pg.Rect(block_size * x, block_size * y, block_size, block_size)
            blocksurface = board_surface.subsurface(blockrect)
            mouse_pos = pg.mouse.get_pos()
            print(mouse_pos)
            mouse_over = blockrect.collidepoint(mouse_pos)
            print(mouse_over)
            await block.draw(blocksurface, highlight=mouse_over)

    async def on_mouse_move(self, event):

        ...