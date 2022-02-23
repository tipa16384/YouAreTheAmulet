# rooms are a truple of (room, x, y)

class Exit:
    def __init__(self, from_room, to_room):
        self.connections = [from_room, to_room]

