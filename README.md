<p align="center"><img src="https://www.sbcar.eu/wp-content/uploads/2018/05/Gdansk-University-of-Technology-loggo.png" width="300" align="middle"></p>

# Intelligent Measuring System
Academic project at Gdansk University of Technology

# Description
Design and implement a measurement system that analyzes data on terrain height variation at points with the highest growth (North and South America). The height increase in a given location should be measured on the basis of 10 measurement points. Find 6 groups of the sink basing on the average growth of altitude. Put detected areas on the map.

## Technologies
Project was created with pyspark ...............

## Dataset
Source dataset: https://registry.opendata.aws/terrain-tiles/. It provides data split into tiles for different zoom values (from 1 to 15). Data are avaliable in four different formats:
- terrarium
    - tiles contain raw elevation data in meters, split into the red, green, and blue channels, with 16 bits of integer and 8 bits of fraction.
- normal
    - tiles are processed elevation data with the the red, green, and blue values corresponding to the direction the pixel “surface” is facing (its XYZ vector).
- geotiff
    - tiles are raw elevation data suitable for analytical use and are optimized to reduce transfer costs.
- skadi
    - tiles are raw elevation data in unprojected WGS84 (EPSG:4326) 1°x1° tiles, used by the Mapzen Elevation lookup service.

For our project we decided to choose terrarium format, as it provides elevation value in each point. To exctract height value, we used formula:

>*height = (red * 256 + green + blue / 256) - 32768*

where *red*, *green* and *blue* are colour channels values.

### Speed of growth
As the aim of our project was to find points with the highest growth, we had to calculate first derivative of height array - the gradient. After testing a few solutions, we observed that the most efficient way is to use *numpy.gradient* function. It is computing gradient using second order accurate central differences in the interior points and either first or second order accurate one-sides (forward or backwards) differences at the boundaries.


### Results
During project, two solutions were prepared: pure-python and pyspark version..............................


Final result - 6 groups based on growth of altitude:
![Final plot](results/gradient_map_groups.png)

Time results for pure-python version:
- laptop:
    - zoom 3 -> 24.741682052612305 seconds
    - zoom 5 -> 202.6480095386505 seconds
- AWS cluster:
    - zoom 3 -> 12.68152517300041 seconds
    - zoom 5 -> 129.09565698999995 seconds

Time results for pyspark version:
- laptop:
    - zoom 3 -> 11.11094856262207 seconds
- AWS cluster:
    - zoom 3 -> 6.148108624999622 seconds


### Conclusion
.......................


#### Project developers (group 9):
* Karol Damaszke
* Bartlomiej Borzyszkowski
