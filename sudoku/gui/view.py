class View:
    def __init__(self):
        self.active = False

    async def start(self):
        self.active = True

    async def end(self):
        self.active = False

    async def update(self, dt):
        ...

    async def draw(self, surface):
        ...

    async def handle_event(self, event):
        ...

    async def on_mouse_move(self, event):
        ...

    async def on_mouse_click(self, event):
        ...

    async def on_key_press(self, event):
        ...
