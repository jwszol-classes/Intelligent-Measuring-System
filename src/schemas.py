from pyspark.sql.types import *


class Schemas:

    @staticmethod
    def struct_result():
        struct_result = StructType([StructField('Coordinates', StringType()),
                                    StructField('Group', StringType()),
                                    StructField('Elevation', StringType())])
        return struct_result

    @staticmethod
    def struct_elevation_data():
        struct_elevation_data = StructType([StructField('Coordinates', StringType()),
                                            StructField('Elevation', StringType())])
        return struct_elevation_data
