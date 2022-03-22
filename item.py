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
    UNARMED = 15

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
        self.sacred = template['sacred'] if 'sacred' in template else False
        self.can_put_on = template['canPutOn'] if 'canPutOn' in template else False
        self.quantity = 1
        self.item_type = eval('ItemType.' + template['itemType'])
        self.cursed_state_known = False
        self.hitchance = 0
        self.damage = "1"
        self.maxHealth = template['maxHealth'] if 'maxHealth' in template else 0
        self.health = self.maxHealth

    def is_vampiric(self):
        return 'vampiric' in self.template and self.template['vampiric']

    def can_block(self):
        return 'blocks' in self.template and self.template['blocks'] and (self.sacred or self.quantity > 0)

    def can_attack(self):
        return self.is_wielded() and (self.sacred or self.quantity > 0)
    
    def attack_with(self):
        if not self.sacred and self.quantity > 0:
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

        if self.sacred:
            name = 'sacred ' + name

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
        
        if self.can_wield() and not self.sacred:
            name += f" ({self.quantity})"

        return name

class MartialArts(Item):
    def __init__(self):
        template = { 'itemType': 'UNARMED', 'item': 'martial arts', 'identified': True, 'canWield': True, 'hitchance': 90, 'damage': '1d1' }
        super().__init__(template)
        self.quantity = 1000000
        self.hitchance = 90
    def __str__(self):
        return 'martial arts'

martialArts = MartialArts()
