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

    async def draw(self, surface):
        x, y = self.x, self.y
        block = surface.get_rect()
        surface.fill(pg.Color("#0ff00f"), block.inflate(-2, -2))
        text = self.font.render(f"{self.cell.value}", True, pg.Color("#0000ff"))
        surface.blit(
            text,
            text.get_rect(center=block.center),
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

    async def draw(self, surface):
        x, y = self.x, self.y
        block = surface.get_rect()
        surface.fill(pg.Color("#000000"), block.inflate(-6, -6))
        text = self.font.render(f"{self.idx}", True, pg.Color("#0000ff"))
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
            await cell.draw(cellsurface)


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
            blocksurface = board_surface.subsurface(
                pg.Rect(block_size * x, block_size * y, block_size, block_size)
            )
            await block.draw(blocksurface)
