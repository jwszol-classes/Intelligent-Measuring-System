"""

Optional commands for configuration of Google Colab:

!apt-get install openjdk-8-jdk-headless -qq > /dev/null
!wget -q https://www-us.apache.org/dist/spark/spark-3.0.1/spark-3.0.1-bin-hadoop2.7.tgz
!tar xf spark-3.0.1-bin-hadoop2.7.tgz
!pip install -q findspark

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.0.1-bin-hadoop2.7"

import findspark
findspark.init()

"""

import matplotlib.pyplot as plt
import numpy as np
import time

from pyspark.sql import SparkSession

# --------------------------------------------- Init session and load data ---------------------------------------------
spark = SparkSession.builder.getOrCreate()
df = spark.read.format("image").load("data")
df_images = df.orderBy("image.origin").select("image.data")

# reshape images (from 1d array)
tiles = []
df_tiles = df_images.take(df_images.count())
for i in range(df_images.count()):
    tile = np.reshape(df_tiles[i][0], (256, 256, 3))
    tiles.append(tile)
# ----------------------------------------------------------------------------------------------------------------------


# ------------------------------- Convert RGB channels to elevation and gradient value ---------------------------------
def rgb_to_meters(rgb):
    height = (rgb[2] * 256.0 + rgb[1] + rgb[0] / 256.0) - 32768.0
    return height if height > 0 else 0


def get_height(curr_tile):
    return np.array([list(map(rgb_to_meters, row)) for row in curr_tile])


start_time = time.time()

tiles_rdd = spark.sparkContext.parallelize(tiles)
height_tiles = tiles_rdd.map(get_height)
grad_arr = np.asarray(height_tiles.map(np.gradient).collect())
# ----------------------------------------------------------------------------------------------------------------------


# -------------------------------------------------- Merge all tiles ---------------------------------------------------
"""
TODO: provide better mechanism for merging tiles
"""
all_tiles = None
for col in range(13):
    col_tiles = None
    for row in range(16):
        arr = grad_arr[col * 16 + row, 0, :, :]
        if col_tiles is None:
            col_tiles = arr
        else:
            col_tiles = np.concatenate((col_tiles, arr), axis=0)

    if all_tiles is None:
        all_tiles = col_tiles
    elif col_tiles is not None:
        all_tiles = np.concatenate((all_tiles, col_tiles), axis=1)

grad_img = abs(all_tiles)
plt.imsave('gradient.png', grad_img, cmap='terrain')
# ----------------------------------------------------------------------------------------------------------------------


# ------------------------------------------- Group points by gradient value -------------------------------------------
def group_value(curr_val):
    for key, val in gradient_groups.items():
        if curr_val < val:
            return int(key)


def grouping(arr_to_group):
    return np.array([group_value(x) for x in arr_to_group])


gradient_groups = {
    0: 2,
    1: 10,
    2: 50,
    3: 150,
    4: 500,
    5: 5000
}

grad_img_rdd = spark.sparkContext.parallelize(grad_img)
grouped_grad_img = np.asarray(grad_img_rdd.map(grouping).collect())
plt.imsave('gradient_groups.png', grouped_grad_img)

stop_time = time.time()
print("Processing time: %s seconds " % (stop_time - start_time))
# ----------------------------------------------------------------------------------------------------------------------
