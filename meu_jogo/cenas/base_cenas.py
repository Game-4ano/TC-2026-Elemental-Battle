class BaseScene:
    def __init__(self, manager):
        self.manager = manager

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        pass