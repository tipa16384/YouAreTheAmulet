from enum import Enum
from random import randint
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
    NECKLACE = 14

class Item:
    def __init__(self, template: dict):
        self.template = template
        self.wielded = False
        self.worn = False
        self.adorned = False
        self.equipped = False
        self.identified = template['identified'] if 'identified' in template else False
        self.isyendor = template['isAmuletOfYendor'] if 'isAmuletOfYendor' in template else False
        self.cursed = template['cursed'] if 'cursed' in template else False
        self.can_put_on = template['canPutOn'] if 'canPutOn' in template else False
        self.quantity = 1
        self.item_type = eval('ItemType.' + template['itemType'])
        self.cursed_state_known = False
        self.hitchance = 0
        self.damage = "1"

    def can_attack(self):
        return self.is_wielded() and self.quantity > 0
    
    def attack_with(self):
        if self.can_attack():
            self.quantity -= 1
    
    def hit(self):
        return randint(1, 100) <= self.hitchance
    
    def roll_damage(self):
        return self.rolldice(self.damage)

    def rolldice(self, dice: str):
        if 'd' in dice:
            n, s = dice.split('d')
            return sum(randint(1, int(s)) for _ in range(int(n)))
        else:
            return int(dice)

    def can_wield(self):
        return 'canWield' in self.template and self.template['canWield']
    
    def is_wielded(self):
        return self.wielded
    
    def is_worn(self):
        return self.worn
    
    def wield(self):
        if self.can_wield() and not self.wielded:
            self.wielded = True
        else:
            self.wielded = False
        return self.wielded
    
    def put_on(self):
        if self.can_put_on and not self.adorned:
            self.adorned = True
            self.cursed_state_known = True
    
    def __str__(self):
        name = self.template['item']

        name = ('an ' if name[0] in 'aeiouAEIOU' else 'a ') + name
        
        if not self.identified:
            name += '?'
        
        if self.cursed_state_known and self.cursed:
            name += '^'

        if self.wielded:
            name += '+'
        
        if self.worn:
            name += '*'
        
        if self.adorned:
            name += '&'
        
        if self.can_wield():
            name += f" ({self.quantity})"

        return name

