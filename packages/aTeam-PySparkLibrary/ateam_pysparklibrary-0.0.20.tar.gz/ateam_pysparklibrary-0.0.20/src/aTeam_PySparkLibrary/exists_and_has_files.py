

#sjekke om delta tabellen har data
def exists_and_has_files(path, spark):
    try:
        # Attempt to read the directory with the format you expect (e.g., 'delta', 'parquet', 'csv')
        df = spark.read.format('delta').load(path)  # Adjust the format as needed
        
        # Check if the DataFrame is empty
        if df.rdd.isEmpty():
            print("Directory exists but contains no files.")
            return False
        else:
            print("Directory exists and contains files.")
            return True
    except Exception as e:
        # If an exception is caught, likely the directory doesn't exist or can't be read as expected
        print(f"Error accessing path: {e}")
        return False