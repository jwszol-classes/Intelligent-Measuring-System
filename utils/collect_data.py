import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
from itertools import product
from math import log, tan, pi

import boto3
import botocore
from botocore import UNSIGNED
from botocore.config import Config

BUCKET_NAME = 'elevation-tiles-prod'   # replace with your bucket name
KEY = 'terrarium/{z}/{x}/{y}.png'    # replace with your object key

s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))

BOUNDS = (72.0, -168.0, -54.0, -25.0)
ZOOM = 3


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
    output_path = './out'
    try:
        for i, (z, x, y) in enumerate(tiles):

            print("Downloading " + str(i+1) + "/" + str(len(tiles)))

            url = KEY.format(z=z, x=x, y=y)
            s3.Bucket(BUCKET_NAME).download_file(url, '{}//{}-{}-{}.png'.format(output_path, z, x, y))

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    except Exception as ex:
        print("Exception occurred: " + str(ex))


def plot_all():
    os.chdir('./out')
    images = os.listdir()
    for img in images:
        print(img)
        im = cv2.imread(img, cv2.IMREAD_UNCHANGED)
        height_arr = np.zeros(im.shape[:2])
        for row in range(im.shape[0]):
            for column in range(im.shape[1]):
                bgr = im[row][column]
                height = (bgr[2] * 256.0 + bgr[1] + bgr[1] / 256.0) - 32768.0
                height_arr[row][column] = height  # if height > 0 else 0

        plt.imshow(height_arr, cmap='terrain')
        plt.colorbar()
        plt.show()


def plot_one():
    os.chdir('./out')
    im = cv2.imread('all.png', cv2.IMREAD_UNCHANGED)
    height_arr = np.zeros(im.shape[:2])
    for row in range(im.shape[0]):
        for column in range(im.shape[1]):
            bgr = im[row][column]
            height = (bgr[2] * 256.0 + bgr[1] + bgr[1] / 256.0) - 32768.0
            height_arr[row][column] = height if height > 0 else 0

    plt.imsave("all2.png", height_arr, cmap='terrain')


def main():
    tiles = get_tiles(ZOOM, *BOUNDS)
    download(tiles)
    # plot_all()
    # plot_one()


if __name__ == '__main__':
    main()
