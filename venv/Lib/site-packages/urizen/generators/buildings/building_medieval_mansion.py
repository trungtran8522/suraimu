#!/usr/bin/python3

import random
from urizen.core.map import Map
from urizen.core.entity_collection import C, T, A

from urizen.generators.rooms.room_default import room_default


def building_medieval_mansion(w=25, h=25, wall_material=None, floor_material=None, direction='down'):
    """
    Construct medieval mansion with living rooms, kitchen, library, treasury, servant's room and outdoor.

    Constraints:

        - Map width and map height must be >= 20
        - Map width and map height must be <= 30
        - Wall material must be 'block', 'plank', 'brick' or 'stone'.
        - Floor material must be 'dirt', 'parquet' or 'cobblestone'.

    Parameters
    ----------
    w : int
        Map width

    h : int
        Map height

    wall_material : str
        Wall's material.

    floor_material : str
        Floor's material.

    direction : str
        Direction of the house. Can be 'up', 'down', 'left' or 'right'.
    """
    # Initial checks. Don't accept too small/big house
    if w < 20 or h < 20:
        raise ValueError('Building is too small: w or h < 20')
    elif w > 30 or h > 30:
        raise ValueError('Building is too big: w or h > 30')
    # Choose materials
    if not wall_material:
        wall_material = random.choice([C.wall_block, C.wall_plank, C.wall_brick, C.wall_stone])
    elif wall_material not in (['block', 'plank', 'brick', 'stone']):
        raise ValueError('Wall material should be "block", "plank", "brick" or "stone"')
    if wall_material == 'block':
        wall_material = C.wall_block
    elif wall_material == 'plank':
        wall_material = C.wall_plank
    elif wall_material == 'brick':
        wall_material = C.wall_brick
    elif wall_material == 'stone':
        wall_material = C.wall_stone

    if not floor_material:
        floor_material = random.choice([C.floor_dirt, C.floor_parquet, C.floor_cobblestone])
    elif floor_material not in (['dirt', 'parquet', 'cobblestone']):
        raise ValueError('Floor material should be "dirt", "parquet" or "cobblestone"')
    if floor_material == 'dirt':
        floor_material = C.floor_dirt
    elif floor_material == 'parquet':
        floor_material = C.floor_parquet
    elif floor_material == 'cobblestone':
        floor_material = C.floor_cobblestone

    M = Map(w, h, fill_cell=C.void)
    default_room_w = w // 4 + 1
    default_room_h = h // 4
    library_h = h // 2 - 1
    second_bedroom_h = h // 4 + 2

    treasury = _room_treasury(default_room_w, default_room_h, wall_material, floor_material)
    M.meld(treasury, 0, 0)
    bedroom = _room_bedroom(default_room_w, h-second_bedroom_h-default_room_h+2, wall_material, floor_material)
    M.meld(bedroom, 0, default_room_h-1)
    second_bedroom = _room_second_bedroom(default_room_w, second_bedroom_h, wall_material, floor_material)
    M.meld(second_bedroom, 0, h-second_bedroom_h)
    sacrifice = _room_of_sacrifice(default_room_w, default_room_h, wall_material, floor_material)
    M.meld(sacrifice, w-default_room_w, 0)
    kitchen = _room_kitchen(default_room_w, h-default_room_h*2+1, wall_material, floor_material)
    M.meld(kitchen, w-default_room_w, default_room_h-1)
    servant = _room_servant(default_room_w, default_room_h+1, wall_material, floor_material)
    M.meld(servant, w-default_room_w, h-default_room_h-1)
    library = _room_library(w-default_room_w*2+2, library_h, wall_material, floor_material)
    M.meld(library, default_room_w-1, 0)
    garden = _interior_garden(w-default_room_w*2, h-library_h, wall_material, floor_material)
    M.meld(garden, default_room_w, library_h)

    if random.choice([True, False]):
        M.hmirror()
    if direction == 'up':
        M.vmirror()
    elif direction == 'left':
        M.transpose()
    elif direction == 'right':
        M.transpose()
        M.hmirror()

    return M


def _room_treasury(w, h, wall_material, floor_material):
    M = room_default(w, h, wall_type=wall_material, floor_type=floor_material)
    items = [
        T.money_pile(),
        T.money_pile(),
        T.necklace(),
        T.mineral_geode(),
        T.mineral_diamond(),
        T.magic_orb(),
        T.scroll_text(),
        T.ring(),
        T.bag(),
    ]
    M.scatter(1, 1, w-1, h-1, items, exclude=[(w-2, h-3)])

    return M


def _room_bedroom(w, h, wall_material, floor_material):
    M = room_default(w, h, wall_type=wall_material, floor_type=floor_material)

    return M


def _room_second_bedroom(w, h, wall_material, floor_material):
    M = room_default(w, h, wall_type=wall_material, floor_type=floor_material)

    return M


def _room_of_sacrifice(w, h, wall_material, floor_material):
    M = room_default(w, h, wall_type=wall_material, floor_type=C.floor_flagged)
    M[w-2, h//2].put(T.magic_portal())
    items = [
        T.effect_blood(),
        T.effect_blood(),
        T.book_magic(),
        T.weapon_dagger(),
        T.bones_remains()
    ]
    M.scatter(1, 1, w-2, h-1, items, exclude=[(1, 2), (w-2, h//2)])

    return M


def _room_kitchen(w, h, wall_material, floor_material):
    M = room_default(w, h, wall_type=wall_material, floor_type=floor_material)

    return M


def _room_servant(w, h, wall_material, floor_material):
    M = room_default(w, h, wall_type=wall_material, floor_type=floor_material)
    for y in range(2, h-1, 2):
        M[1, y].put(T.furniture_bed_single())
    
    num_table = 1 if h < 8 else h - 3
    for y in (1, num_table):
        M[w-2, y].put(T.furniture_table_round())
        M[w-3, y].put(T.furniture_stool())
        M[w-2, y+1].put(T.furniture_stool())
    items = [
        T.light_torch(),
        T.furniture_cabinet(),
        T.furniture_chest_profile()
    ]
    M.scatter(1, h-3, w-1, h-1, items)
    M[2, 0] = C.door_closed_window()

    return M


def _room_library(w, h, wall_material, floor_material):
    M = room_default(w, h, wall_type=wall_material, floor_type=floor_material)

    return M


def _interior_garden(w, h, wall_material, floor_material):
    M = Map(w, h, fill_cell=C.floor_rocks)
    for x in range(w):
        M[x, h-1] = wall_material()
    M[w//2, h-1] = C.door_closed_wooden()
    M[w//2-1, h-1] = C.door_closed_wooden()

    return M
