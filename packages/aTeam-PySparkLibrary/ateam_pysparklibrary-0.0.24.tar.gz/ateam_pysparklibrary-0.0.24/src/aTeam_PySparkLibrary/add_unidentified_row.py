### author: Martin Nenseth / Ludvig Løite


from aTeam_PySparkLibrary.exists_and_has_files import exists_and_has_files

from pyspark.sql import SparkSession
from delta import *
from pyspark.sql.types import *
from delta.tables import *
from pyspark.sql.functions import *

def add_unidentified_row(directoryLevel, folderPath, businessKeyColumn, primaryKeyColumn, storageAccName, debugBool, spark):


    if debugBool:
        fullPath = f"data/{directoryLevel}/{folderPath}"
    else:
        fullPath = f"abfss://{directoryLevel}@{storageAccName}.dfs.core.windows.net/{folderPath}"
    print("full path: ",fullPath)

    #Sjekke om det finnes en tabell fra før
    if exists_and_has_files(fullPath, spark): 
        print('Delta table exists.')

        #Lese inn eksisterende tabell hvor det er en ukjent rad.
        original = spark.read.format("delta").load(fullPath).where(f"'{primaryKeyColumn}' = -1")  

        print("ORigianl table:",spark.read.format("delta").load(fullPath).where("'pk_dim_property_management_group_key' == -1").show())

        #Hvis tabellen ikke inneholder ukjent rad
        if original.count() == 0: 
            
            #Tom liste som skal populeres med data for tom rad
            data = list() 

            #Iterasjon av kolonne oppsett / tabell-schema
            for column in original.schema: 

                #Opprette ukjent-data for bedriftsnøkkel kolonnen
                if column.name == businessKeyColumn: 
                    data.append('-1')

                #Opprette ukjent-data for primærnøkkel kolonnen 
                elif column.name == primaryKeyColumn: 
                    data.append('-1')

                #Endre kilde til Synapse 
                elif column.name == 'source': 
                    data.append('Synapse')

                #Fastsatte verdier for variabel type og navn type
                else: 
                
                    if str(column.dataType) == "StringType":
                            data.append('Ukjent')
                    else:
                        data.append(None)
                    print(column.name, '  = ', None)

            #Slå sammen schema og data for å skape en DataFrame som kan sendes inn på toppen av eksisterende tabell 
            df = spark.createDataFrame(data=[data],schema=original.schema)

            #Legger til tidspunktet for denne kjørings som oppdatertingstidspunkt i tabellen
            df = df.withColumn('updated_utc', current_timestamp())

            #Se den nyopprettede DataFramen      
            df.show()  

            #Skrive tilbake til original URL basert på path
            df.write.format("delta").mode("append").option("mergeSchema", "true").save(fullPath) 
            print('Empty row added to delta table.')
        else:
            print('Empty row already exist.')
    else:
        print('Delta table does not exist.')
        raise Exception(f'Delta table does not exist.')        
        




directoryLevel = 'silver'
folderPath = "Dimensions/PropertyManagementGroup/"
businessKeyColumn  = "asset_id"
dimensionKeyColumn = "pk_dim_property_management_group_key"
storageAccName = "pedataplatformdev" #TODO: retrieve from key vault
debugBool = True

builder = SparkSession.builder.appName("debugSession").config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

add_unidentified_row(directoryLevel, folderPath, businessKeyColumn, dimensionKeyColumn, storageAccName, debugBool, spark)
spark.stop()