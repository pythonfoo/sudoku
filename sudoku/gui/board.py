from .view import View
from ..field import Field
import pygame as pg


class Block(View):
    def __init__(self, x, y, field):
        self.field = field
        self.x = x
        self.y = y
        self.idx = 3 * y + x
        self.font = pg.font.SysFont("Vera", 42)

    async def draw(self, surface):
        x, y = self.x, self.y
        block = surface.get_rect()
        surface.fill(pg.Color("#0ff00f"), block.inflate(-6, -6))
        text = self.font.render(f"{self.idx}", True, pg.Color("#0000ff"))
        surface.blit(
            text,
            text.get_rect(center=block.center),
        )


class Board(View):
    def __init__(
        self,
    ):
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
