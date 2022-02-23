class Floor:
    def __init__(self, floor_name):
        self.floor_name = floor_name
        self.rooms = []
        self.exits = []

    def get_floor_name(self):
        return self.floor_name
    
    def get_rooms(self):
        return self.rooms
    
    def add_room(self, room):
        self.rooms.append(room)
    
    def __str__(self):
        return self.floor_name
    
    def __repr__(self):
        return self.floor_name
