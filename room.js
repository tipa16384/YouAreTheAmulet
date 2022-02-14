/**
 * ROOM
 * 
 * a Javascript class for a room
 */

class Room {
    constructor (name, description, exits, items, npcs, players) {
        this.name = name;
        this.description = description;
        this.exits = exits;
        this.items = items;
        this.npcs = npcs;
        this.players = players;
    }
}