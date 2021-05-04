#!/usr/bin/python3

import random
from math import sqrt
from copy import deepcopy
import itertools as it
from urizen.core.map import Map
from urizen.core.entity_collection import C

P = {
    0: C.overworld_forest,
    1: C.overworld_ocean,
    2: C.overworld_steppe,
    3: C.overworld_shrubland,
    4: C.overworld_ocean,
    5: C.wall_stone,
    6: C.wall_plank,
    7: C.fire,
    8: C.flora_cactus,
    9: C.overworld_forest_boreal,
    10: C.overworld_forest,
    11: C.overworld_ocean,
    12: C.overworld_steppe,
    13: C.overworld_shrubland,
    14: C.overworld_ocean,
    15: C.wall_stone,
    16: C.wall_plank,
    17: C.fire,
    18: C.flora_cactus,
    19: C.overworld_forest_boreal,
    20: C.overworld_forest,
    21: C.overworld_ocean,
    22: C.overworld_steppe,
    23: C.overworld_shrubland,
    24: C.overworld_ocean,
    25: C.wall_stone,
    26: C.wall_plank,
    27: C.fire,
    28: C.flora_cactus,
    29: C.overworld_forest_boreal,
}

def world_test2(w=400, h=200):
    M = Map(w, h, fill_cell=C.overworld_ocean)
    '''
    plates = {i: (random.randint(0, w-1), random.randint(0, h-1)) for i in range(30)}
    for y, line in enumerate(M.cells):
        for x, cell in enumerate(line):
            intervals = {i: (plates[i][0] - x) ** 2 + (plates[i][1] - y) ** 2 for i in plates}
            #print(intervals)
            M[x, y].plate = min(intervals.items(), key=lambda item: item[1])[0]
    for y, line in enumerate(M.cells):
        for x, cell in enumerate(line):
            M[x, y] = P[M[x, y].plate]()
    for i in plates:
        M[plates[i]] = C.void()
    '''
    for y, line in enumerate(M.cells):
        for x, cell in enumerate(line):
            distance_corners = min([
                sqrt(x**2 + y**2),
                sqrt((w-x)**2 + y**2),
                sqrt(x**2 + (h-y)**2),
                sqrt((w-x)**2 + (h-y)**2)
            ])
            distance_edges = min([x, y, (w-x), (h-y)])
            minus = (w + h) / 3
            c = random.randint(-w*0.8, -w*0.6) + distance_corners + distance_edges
            #print('{:> .1f}'.format(c), '', end='')
            M[x, y] = C.overworld_ocean() if c < 0 else C.overworld_forest()
        #print()
    #for y in [0, h-1]:
    #    for x in range(M.w):
    #        M[x, y] = C.overworld_ocean()
    #for x in [0, w-1]:
    #    for y in range(M.h):
    #        M[x, y] = C.overworld_ocean()
    #for x in range(w//2-2, w//2+3):
    #    for y in range(h//2-2, h//2+3):
    #        M[x, y] = C.overworld_forest()
    
    #for y, line in enumerate(M.cells):
    #    for x, cell in enumerate(line):
    #        if sum(c.cname == 'overworld_forest' for c in M.surrounding(x, y)) >= 7:
    #            M[x, y] = C.overworld_forest()
    #M = _smooth_map(M)

    return M



def world_test(w, h):
    heightmap = []
    for y in range(h):
        line = []
        for x in range(w):
            distance_corners = min([
                sqrt(x**2 + y**2),
                sqrt((w-x)**2 + y**2),
                sqrt(x**2 + (h-y)**2),
                sqrt((w-x)**2 + (h-y)**2)
            ])
            distance_edges = min([x*0.7, y*0.7, (w-x)*0.7, (h-y)*0.7])
            minus = (w + h) / 3
            c = random.randint(-w*0.7, -w*0.6) + distance_corners + distance_edges
            #print('{:> .1f}'.format(c), '', end='')
            line.append(c)
        heightmap.append(line)
    heightmap = diamond_square_2x(heightmap)
    heightmap = diamond_square_2x(heightmap, smooth_iteration=2)
    heightmap = diamond_square_2x(heightmap, smooth_iteration=3)
    heightmap = diamond_square_2x(heightmap, smooth_iteration=4)

    M = Map(len(heightmap[0]), len(heightmap), fill_cell=C.overworld_ocean)
    for y, line in enumerate(M.cells):
        for x, cell in enumerate(line):
            M[x, y] = C.overworld_ocean() if heightmap[y][x] < 0 else C.overworld_forest()
    
    M = _smooth_map(M)
    M = _smooth_map(M)
    return M


def diamond_square_2x(heightmap, smooth_iteration=1):
    #from pprint import pprint
    hm = deepcopy(heightmap)
    for i, line in enumerate(hm):
        hm[i] = list(it.chain.from_iterable([h, None] for h in line))
    hm = list(it.chain.from_iterable([line, [None] * len(hm[0])] for line in hm))
    for i, line in enumerate(hm):
        hm[i] = line[:-1]
    hm = hm[:-1]
    for j, line in enumerate(hm[1::2]):
        for i, cell in enumerate(line[1::2]):
            x = 2 * i + 1
            y = 2 * j + 1
            hm[y][x] = sum([
                hm[y-1][x-1],
                hm[y-1][x+1],
                hm[y+1][x-1],
                hm[y+1][x+1],
            ]) / 4 + ((random.random() - 0.5) * 2 / smooth_iteration)
    for y, line in enumerate(hm):
        for x, cell in enumerate(line):
            if hm[y][x] == None:
                bordering = []
                if y > 0:
                    bordering.append(hm[y-1][x])
                if y < len(hm) - 1:
                    bordering.append(hm[y+1][x])
                if x > 0:
                    bordering.append(hm[y][x-1])
                if x < len(hm[0]) - 1:
                    bordering.append(hm[y][x+1])
                hm[y][x] = sum(bordering) / len(bordering) + ((random.random() - 0.5) * 2 / smooth_iteration)

    return hm


def _smooth_map(M):
    """
    Smooth a map using cellular automata.

    If number of walls around the cell (including it) is more than number of floors, replace the cell with a wall.
    In other case replace the cell with a floor.
    """

    # Already replaced cells must not affect current so we need a copy of the original map 
    M2 = deepcopy(M)
    for y, line in enumerate(M2.cells[1: -1]):
        for x, _ in enumerate(line[1: -1]):
            true_x = x + 1
            true_y = y + 1
            # Check the number of walls in ORIGINAL map
            number_of_walls = sum(
                cell.cname == 'overworld_forest'
                for cell in [
                    M.cells[true_y][true_x],
                    M.cells[true_y+1][true_x],
                    M.cells[true_y-1][true_x],
                    M.cells[true_y][true_x+1],
                    M.cells[true_y+1][true_x+1],
                    M.cells[true_y-1][true_x+1],
                    M.cells[true_y][true_x-1],
                    M.cells[true_y+1][true_x-1],
                    M.cells[true_y-1][true_x-1],
                ]
            )
            # And set them in smoothed map
            M2.cells[true_y][true_x] = (
                C.overworld_forest()
                if number_of_walls >= 5
                else C.overworld_ocean()
            )
    return M2