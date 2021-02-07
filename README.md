<p align="center"><img src="https://www.sbcar.eu/wp-content/uploads/2018/05/Gdansk-University-of-Technology-loggo.png" width="300" align="middle"></p>

# Intelligent Measuring System
Academic project at Gdansk University of Technology

# Description
Design and implement a measurement system that analyzes data on terrain height variation at points with the highest growth (North and South America). The height increase in a given location should be measured on the basis of 10 measurement points. Find 6 groups of the sink basing on the average growth of altitude. Put detected areas on the map.

## Technologies
The project aimed to use cloud technologies for the efficient processing of large data sets. For this purpose, the Amazon Web Services (AWS) platform was used, on which the experiments were launched with utilization of a computing cluster. The performance of a measurement system in terms of computing time was compared with a local execution on laptop. In context of cloud computing, we defined the following technological requirements:

* Account on [www.awseducate.com](http://www.awseducate.com/ "http://www.awseducate.com") ($50 credit available for project purposes)
* Single node EMR cluster on AWS with EMR 5.32.0
* Cluster software configuration: Spark 2.4.7 on Hadoop 2.10.1 YARN and Zeppelin 0.8.2
* Cluster hardware configuration: m5.xlarge
* Configuration of SSH access to the cluster based on EC2 key pair
* S3 cloud storage with source data `s3://elevation-tiles-prod/`


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

## Speed of growth
As the aim of our project was to find points with the highest growth, we had to calculate first derivative of height array - the gradient. After testing a few solutions, we observed that the most efficient way is to use *numpy.gradient* function. It is computing gradient using second order accurate central differences in the interior points and either first or second order accurate one-sides (forward or backwards) differences at the boundaries.


## Results
During project, two solutions were prepared: pure-python and pyspark version 2.4.7


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


## Conclusion

Our results show successful, comprehensive data analysis on terrain height variation at points with the highest growth on the selected region (North and South America). We find and present 6 groups of the elevation and mark them with corresponding colors on the map, using different zooms for increased precision of measurements.

Possibilities that we get thanks to a presented approach to data filtering in the cloud are very convenient. We are capable of retrieving required values from big set of data in a very short time. Our performance measurements show that the time of data processing at AWS is around twice faster than while using a personal laptop. Moreover, we are able to benefit from parallel processing of data in batch systems in PySpark which gives us further double acceleration of system while keeping the same, expected results of analysis.

Moreover, the main advantage of the presented approach is its high scalability, universality and reliability. Thanks to access to a cloud environment, we are able to easily increase the resources of our cluster, e.g. by adding more instances (nodes) or by using more efficient computing units (up to m5.24xlarge instances at AWS). Furthermore, we benefit from great software scalability of PySpark which brings robust and cost-effective ways to filter huge data collections in the cloud. On the other hand, we're able to quickly and easily reconfigure our environment and use the computing resources only when necessary and therefore lead to massive cost savings. The entire process is very user-friendly even for beginners thanks to a well-supported community and environment of AWS.


#### Project developers (group 9):
* Karol Damaszke
* Bartlomiej Borzyszkowski
