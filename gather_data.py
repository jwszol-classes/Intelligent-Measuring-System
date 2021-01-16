import warnings
import matplotlib.pyplot as plt
import numpy as np
from podpac.datalib.terraintiles import TerrainTiles
from podpac import Coordinates, clinspace


warnings.filterwarnings('ignore')

def get_terrain_tiles():
    """ Get Tiles from S3 with Podpac library """

    # Create coordinates to get tiles of both North and South Americas
    node = TerrainTiles(tile_format='geotiff', zoom=5)
    coords = Coordinates([clinspace(75, -60, 1000), clinspace(-155, -35, 1000)], dims=['lat', 'lon'])

    # Evaluate node
    ev = node.eval(coords)
    data = np.asarray(ev.data)
    return data

def main():
    data = get_terrain_tiles()
    plt.imshow(data)
    plt.savefig("./data_unprocessed.png")


if __name__ == '__main__':
    main()
