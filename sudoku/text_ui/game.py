import asyncio

"""
A Textual app to create a fully working calculator, modelled after MacOS Calculator.
"""

from decimal import Decimal

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.padding import Padding
from rich.text import Text
from textual.app import App
from textual.reactive import Reactive
from textual.views import GridView
from textual.widget import Widget
from textual.widgets import Button, ButtonPressed


class Cell(Button):
    def on_enter(self) -> None:
        # self.label = ""
        self.style = "reverse"

    def on_leave(self) -> None:
        self.style = "bold"


class Block(GridView):
    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    def on_mount(self) -> None:
        self.buttons = {
            "1": Cell("1"),
            "2": Cell("2"),
            "3": Cell("3"),
            "4": Cell("4"),
            "5": Cell("5"),
            "6": Cell("6"),
            "7": Cell("7"),
            "8": Cell("8"),
            "9": Cell("9"),
        }

        # set grid
        self.grid.add_column("col", repeat=3)
        self.grid.add_row("row", repeat=3)

        self.grid.place(*self.buttons.values())


class Game(GridView):
    def on_mount(self) -> None:
        self.buttons = {
            "1": Block(),
            "2": Block(),
            "3": Block(),
            "4": Block(),
            "5": Block(),
            "6": Block(),
            "7": Block(),
            "8": Block(),
            "9": Block(),
        }

        # set grid
        self.grid.set_gap(2, 1)
        self.grid.set_gutter(1)
        self.grid.add_column("col", size=15, repeat=3)
        self.grid.add_row("row", size=9, repeat=3)

        self.grid.place(*self.buttons.values())


class GameApp(App):
    async def on_mount(self) -> None:
        await self.view.dock(Game())

    async def on_load(self, event):
        await self.bind("q", "quit")


def main():
    GameApp.run(title="Sudoku Test", log="textual.log")


if __name__ == "__main__":
    main()
