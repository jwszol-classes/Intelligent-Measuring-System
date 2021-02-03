<p align="center"><img src="https://www.sbcar.eu/wp-content/uploads/2018/05/Gdansk-University-of-Technology-loggo.png" width="300" align="middle"></p>

## Intelligent Measuring System

Academic project at Gdansk University of Technology

### Topic 5 - description

Design and implement a measurement system that analyzes data on terrain height variation at points with the highest growth (North and South America). The height increase in a given location should be measured on the basis of 10 measurement points. Find 6 groups of the sink basing on the average growth of altitude. Put detected areas on the map.

#### Source dataset:
https://registry.opendata.aws/terrain-tiles/

#### Additional information:

Recommended technologiese: EMR/Spark/Python/Scala/Java

Results should be presented in a graphic form, using a chosen library

#### Project developers (group 9):
* Karol Damaszke
* Bartlomiej Borzyszkowski



## Project Report

> The main goal of this project was to implement a measurment system, run it at Amazon Web Services (AWS) and observe its performance.

#### Requirements
* account on [www.awseducate.com](http://www.awseducate.com/ "http://www.awseducate.com")
* single node EMR cluster on AWS
* cluster software configuration: Spark 2.4.7 on Hadoop 2.10.1 YARN and Zeppelin 0.8.2
* cluster hardware configuration: m5.xlarge
* S3 cloud storage with source data `s3://elevation-tiles-prod/`
