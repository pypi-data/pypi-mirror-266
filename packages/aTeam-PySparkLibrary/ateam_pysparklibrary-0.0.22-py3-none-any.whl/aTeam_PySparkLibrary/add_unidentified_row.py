### Kontaktperson: Martin Nenseth / Ludvig Løite


from aTeam_PySparkLibrary.exists_and_has_files import exists_and_has_files


from pyspark.sql.functions import *

def add_unidentified_row(directoryLevel, folderPath, businessKeyColumn, primaryKeyColumn, storageAccName, spark):

    fullPath = f"abfss://{directoryLevel}@{storageAccName}.dfs.core.windows.net/{folderPath}"
    print(fullPath)

    #Sjekke om det finnes en tabell fra før
    if exists_and_has_files(fullPath, spark): 
        print('Delta table exists.')

        #Lese inn eksisterende tabell hvor det er en ukjent rad.
        original = spark.read.format("delta").load(fullPath).where(f"'{primaryKeyColumn}' = -1")  

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
        