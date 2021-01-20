import os
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import *
from schemas import Schemas


os.chdir('../utils/out')
filenames = os.listdir()
filenames.sort()
print(filenames)

context = SparkContext()
context_sql = SQLContext(context)
results = []

for filename in filenames:

    print(filename)
    lines = context.textFile(filename)
    records = lines.map(lambda l: l.split(","))

    schema = Schemas.struct_elevation_data()
    file = context_sql.createDataFrame(records, schema)

    coordinates = file.select(col('Coordinates')).collect()[0]['Coordinates']
    elevation = file.select(col('Elevation')).collect()[0]['Elevation']

    results.append([filename, cooridinates, elevation])

context_sql.createDataFrame(results, Schemas.struct_result()).write.csv('s3://terrain_tiles/results/')
context.stop()
