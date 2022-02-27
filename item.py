from enum import Enum

class ItemType(Enum):
    WAND = 1
    SWORD = 2
    SHIELD = 3
    POTION = 4
    RING = 5
    BOOTS = 6
    HELMET = 7
    ARMOR = 8
    AMULET = 9
    BOW = 10
    POLEARM = 11
    STAFF = 12
    FOOD = 13

class Item:
    def __init__(self, template: dict):
        self.template = template
        self.wielded = False
        self.worn = False
        self.equipped = False
        self.identified = False
        self.cursed = False
        self.quantity = 1
        self.item_type = eval('ItemType.' + template['itemType'])

    def can_wield(self):
        return 'canWield' in self.template and self.template['canWield']
    
    def is_wielded(self):
        return self.wielded
    
    def wield(self):
        if self.can_wield() and not self.wielded:
            self.wielded = True
    
    def __str__(self):
        name = self.template['item']
        if not self.identified:
            name = 'unidentified ' + name
        elif self.cursed:
            name = 'cursed ' + name

        if self.quantity != 1:
            name = f"{self.quantity} {name}s"
        else:
            name = ('an ' if name[0] in 'aeiouAEIOU' else 'a ') + name

        return name

