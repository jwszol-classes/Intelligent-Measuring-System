import os
from itertools import product
from math import log, tan, pi
import shutil

import boto3
import botocore
import cv2
import matplotlib.pyplot as plt
import numpy as np
import skimage.measure
from botocore import UNSIGNED
from botocore.config import Config

BUCKET_NAME = 'elevation-tiles-prod'
KEY = 'terrarium/{z}/{x}/{y}.png'

ZOOM = 4
BOUNDS = (72.0, -168.0, -54.0, -25.0)   # North and South America

OUTPUT_PATH = 'out'


def mercator(lat, lon, zoom):
    """
    Convert latitude, longitude to z/x/y tile coordinate at given zoom.
    """
    # convert to radians
    x1, y1 = lon * pi / 180, lat * pi / 180

    # project to mercator
    x2, y2 = x1, log(tan(0.25 * pi + 0.5 * y1))

    # transform to tile space
    tiles, diameter = 2 ** zoom, 2 * pi
    x3, y3 = int(tiles * (x2 + pi) / diameter), int(tiles * (pi - y2) / diameter)

    return zoom, x3, y3


def get_tiles(zoom, lat1, lon1, lat2, lon2):
    """
    Convert geographic bounds into a list of tile coordinates at given zoom.
    """
    # convert to geographic bounding box
    min_lat, min_lon = min(lat1, lat2), min(lon1, lon2)
    max_lat, max_lon = max(lat1, lat2), max(lon1, lon2)

    # convert to tile-space bounding box
    _, x_min, y_min = mercator(max_lat, min_lon, zoom)
    _, x_max, y_max = mercator(min_lat, max_lon, zoom)

    # generate a list of tiles
    xs, ys = range(x_min, x_max + 1), range(y_min, y_max + 1)
    tiles = [(zoom, x, y) for (y, x) in product(ys, xs)]

    return tiles


def download(tiles):
    """
    Download given tiles from S3 bucket
    """
    try:
        s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))

        for i, (z, x, y) in enumerate(tiles):
            print("Downloading " + str(i + 1) + "/" + str(len(tiles)))

            url = KEY.format(z=z, x=x, y=y)
            s3.Bucket(BUCKET_NAME).download_file(url, '{}\\{}-{}-{}.png'.format(OUTPUT_PATH, z, x, y))

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    except Exception as ex:
        print("Exception occurred: " + str(ex))
        raise


# -------- helper functions for sorting --------
def sort_by_col(name):
    return int(name.split('.')[0].split('-')[1])


def sort_by_row(name):
    return int(name.split('.')[0].split('-')[2])
# ----------------------------------------------


def merge_all():
    """
    Merge all tiles for given zoom into one
    """
    os.chdir(OUTPUT_PATH)

    # get all tiles and sort them
    tiles_names_all = os.listdir()
    tiles_names_all = sorted(tiles_names_all, key=sort_by_col)

    # get number of first column
    first_col_num = int(tiles_names_all[0].split('-')[1])

    # split tiles names by cols
    tiles_names = []
    rows = []
    for tile in tiles_names_all:
        zoom, col, row = tile.split('.')[0].split('-')
        if int(row) not in rows:
            tiles_names.append([])
            rows.append(int(row))
        tiles_names[int(col) - first_col_num].append(tile)

    # merge all tiles into one
    all_tiles = None
    for col in tiles_names:
        col = sorted(col, key=sort_by_row)
        col_tiles = None
        for row in col:
            im = cv2.imread(row, cv2.IMREAD_UNCHANGED)
            if col_tiles is None:
                col_tiles = im
            else:
                col_tiles = np.concatenate((col_tiles, im), axis=0)

        if all_tiles is None:
            all_tiles = col_tiles
        elif col_tiles is not None:
            all_tiles = np.concatenate((all_tiles, col_tiles), axis=1)

    cv2.imwrite("all.png", all_tiles)
    os.chdir('..')


def plot_maps():
    """
    Convert each pixel from RGB to elevation. Display image
    """
    os.chdir(OUTPUT_PATH)
    im = cv2.imread('all.png', cv2.IMREAD_UNCHANGED)
    height_arr = np.zeros(im.shape[:2])

    for row in range(im.shape[0]):
        for column in range(im.shape[1]):
            bgr = im[row][column]
            height = (bgr[2] * 256.0 + bgr[1] + bgr[1] / 256.0) - 32768.0
            height_arr[row][column] = height if height > 0 else 0

    os.chdir('..')

    # normal map
    plot_and_save(height_arr, "Height map", "height_map.png", 'terrain')

    # normal map with pooling
    pool_height_arr = skimage.measure.block_reduce(height_arr, (3, 3), np.mean)
    plot_and_save(pool_height_arr, "Height map with pooling", "height_map_pooling.png", 'terrain')

    # normal map split into groups
    height_groups = {
        0: 5,
        1: 100,
        2: 500,
        3: 1200,
        4: 2800,
        5: 8000,
    }
    height_arr_groups = get_groups(height_arr, height_groups)
    plot_and_save(height_arr_groups, "Height map groups", "height_map_groups.png")
    pool_height_arr_groups = get_groups(pool_height_arr, height_groups)
    plot_and_save(pool_height_arr_groups, "Height map groups with pooling", "height_map_groups_pooling.png")

    # gradient
    gradient_arr = abs(np.gradient(height_arr, axis=1))
    plot_and_save(gradient_arr, "Gradient map", "gradient_map.png", 'terrain')

    # gradient groups
    gradient_groups = {
        0: 2,
        1: 10,
        2: 50,
        3: 150,
        4: 500,
        5: 5000
    }
    gradient_arr_groups = get_groups(gradient_arr, gradient_groups)
    plot_and_save(gradient_arr_groups, "Gradient map groups", "gradient_map_groups.png")

    plt.show()


def plot_and_save(arr, title, file_name, cmap=None):
    plt.figure()
    plt.imsave(file_name, arr, cmap=cmap)
    plt.imshow(arr)
    plt.title(title)


def get_groups(arr, groups):
    groups_arr = np.zeros(arr.shape)
    for row in range(arr.shape[0]):
        for column in range(arr.shape[1]):
            for key, val in groups.items():
                if arr[row][column] < val:
                    groups_arr[row][column] = int(key)
                    break

    return groups_arr


def main():
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH)

    os.mkdir(OUTPUT_PATH)

    tiles = get_tiles(ZOOM, *BOUNDS)
    download(tiles)
    merge_all()
    plot_maps()


if __name__ == '__main__':
    main()
