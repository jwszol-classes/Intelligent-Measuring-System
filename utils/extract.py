import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

import boto3
import botocore
from botocore import UNSIGNED
from botocore.config import Config

os.chdir('./out')

# get tiles names and separate them
tiles_names_all = os.listdir()
tiles_names_all.sort()
print(tiles_names_all)

tiles_names = []
for tile in tiles_names_all:
    zoom, col, row = tile.split('.')[0].split('-')
    if int(row) == 1:
        tiles_names.append([])
    tiles_names[int(col)].append(tile)

# merge all tiles into one
all_tiles = None
for col in tiles_names:
    col_tiles = None
    for row in col:
        im = cv2.imread(row, cv2.IMREAD_UNCHANGED)
        if col_tiles is None:
            col_tiles = im
        else:
            col_tiles = np.concatenate((col_tiles, im), axis=0)

    if all_tiles is None:
        all_tiles = col_tiles
    else:
        all_tiles = np.concatenate((all_tiles, col_tiles), axis=1)


cv2.imwrite("all.png", all_tiles)
