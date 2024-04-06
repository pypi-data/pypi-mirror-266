### Kontaktperson: Martin Nenseth / Ludvig Løite


from aTeam_PySparkLibrary.exists_and_has_files import exists_and_has_files

from pyspark.sql import functions as F
from pyspark.sql.functions import coalesce, explode, row_number
from pyspark.sql.window import Window


def perform_delta_load(storage_account_name, bronze_path, file_extension, dataset_type, dataset_name, business_key_column_name, spark):

    print("Performing delta load for dataset ",dataset_type,'_', dataset_name,", using ", business_key_column_name, " as business key")
    
    full_silver_path = ""

    full_bronze_path = f"abfss://bronze@{storage_account_name}.dfs.core.windows.net/{bronze_path}"

    if dataset_type == "dim":
        full_silver_path = f"abfss://silver@{storage_account_name}.dfs.core.windows.net/Dimensions/Delta_executed/{dataset_name.capitalize()}/"

    elif dataset_type == "fact":
        full_silver_path = f"abfss://silver@{storage_account_name}.dfs.core.windows.net/Facts/Delta_executed/{dataset_name.capitalize()}/"

    else:
        print("Dataset type is wrong.")
        raise Exception(f'Dataset type is wrong.') 

    print("full bronze path: ",full_bronze_path)

    if file_extension == 'csv':
        bronze_df = spark.read.option("header", "true").csv(full_bronze_path)
        #remove whitespace in column names
        bronze_df = bronze_df.toDF(*[col.replace(" ", "") for col in bronze_df.columns])
    elif file_extension == 'parquet':
        bronze_df = spark.read.parquet(full_bronze_path)
    elif file_extension == 'json': #assumes data to be flattened is located in column "data"
        bronze_df = spark.read.json(full_bronze_path)
        flattened_df = bronze_df.select(explode(bronze_df['data']).alias('exploded_column'))
    else:
        print("File extension not supported")
        raise Exception(f'File extension not supported.')

    def create_select_expression(dataset_key_name):
        column_names = []
        for col in bronze_df.dtypes:
            column_names.append(col[0])

        select_exprs = []
        for column in column_names:
            select_exprs.append(coalesce(f"bronze_{column}", f"silver_{column}").alias(column))

        select_exprs.append(dataset_key_name)
        return select_exprs


    dataset_key_name = 'silver_pk_' + dataset_type + '_' + dataset_name + '_key'

    print("checking if delta load exist here:" ,f"{full_silver_path}_delta_log")
    
    if(exists_and_has_files(full_silver_path, spark)):
        print("Dataset already exists, executing delta load")
        silver_dataset_df = spark.read.format('delta').load(full_silver_path)

        bronze_df_alias_prefix = bronze_df.select([F.col(c).alias("bronze_"+c) for c in bronze_df.columns])
        silver_df_alias_prefix = silver_dataset_df.select([F.col(c).alias("silver_"+c) for c in silver_dataset_df.columns])

        joined = bronze_df_alias_prefix.join(silver_df_alias_prefix, bronze_df_alias_prefix['bronze_' + business_key_column_name] == silver_df_alias_prefix['silver_' + business_key_column_name], how='full_outer')

        select_expression = create_select_expression(dataset_key_name)
        merged = joined.select(select_expression)

        max_key = merged.selectExpr(f"max({dataset_key_name}) as key").collect()[0].key

        new_rows_without_key = merged.filter(merged[dataset_key_name].isNull())

        new_rows_array = []
        for row in new_rows_without_key.collect():
            max_key = max_key + 1
            row_dict = row.asDict()
            row_dict[dataset_key_name] = max_key
            
            new_rows_array.append(tuple(row_dict.values()))
        
        new_rows_with_generated_key = spark.createDataFrame(new_rows_array, merged.schema)

        #combine new rows with existing
        upserted_rows = merged.filter(merged[dataset_key_name].isNotNull()).union(new_rows_with_generated_key)

        upserted_rows_without_prefix_column_names = upserted_rows.withColumnRenamed(dataset_key_name, dataset_key_name.replace('silver_', ''))

        fixedSchema = spark.createDataFrame(upserted_rows_without_prefix_column_names.collect(), schema=silver_dataset_df.schema)


        #TODO: Validate unique business and dataset keys
        fixedSchema.write.format('delta').mode("overwrite").save(full_silver_path)

        print("Delta load executed. Silver path: ", full_silver_path)
        #maybe do som validation
    else:
        print("Dataset does not exists in silver, create it for the first time")
        #create unique ids for all rows in bronze_df
        window_spec = Window.orderBy(business_key_column_name)
        df_with_consecutive_id = bronze_df.withColumn(dataset_key_name.replace('silver_', ''), row_number().over(window_spec) - 1)

        #write to silver
        df_with_consecutive_id.write.format('delta').mode("append").option("overwriteSchema", "true").save(full_silver_path)
        print("Dataset created for the first time. Silver path: ", full_silver_path)