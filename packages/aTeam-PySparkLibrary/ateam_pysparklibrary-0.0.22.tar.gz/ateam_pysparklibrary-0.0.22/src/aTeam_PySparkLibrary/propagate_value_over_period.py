#### Kontaktperson: Ludvig Løite


from pyspark.sql.functions import  lit
import pandas as pd
from pandas.tseries.offsets import MonthEnd, 
from datetime import timedelta
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from copy import deepcopy


storage_account_name = "pedataplatformdev"
silver_path = "Facts/tmp/PropertyEnergyLabelNonMonthly"
new_silver_path = "Facts/PropertyEnergyLabel"

start_date_column_in_input_table = "issuedDate"
end_date_column_in_input_table = "expireDate"
business_key_in_input_table = "asset_id"

date_column_in_output_table = "first_date_in_month"

def propagate_value_over_period(storage_account_name, silver_path, new_silver_path,start_date_column_in_input_table, end_date_column_in_input_table, business_key_in_input_table, date_column_in_output_table, spark):

    full_silver_path = f"abfss://silver@{storage_account_name}.dfs.core.windows.net/{silver_path}/"
    full_new_silver_path = f"abfss://silver@{storage_account_name}.dfs.core.windows.net/{new_silver_path}/"

    silver_df = spark.read.format("delta").load(full_silver_path)
    silver_df_new = silver_df.withColumn(date_column_in_output_table, lit(None))

    silver_pd_df = silver_df_new.toPandas()

    # Forklaring av koden under:
    # Vi ønsker å gjøre om en rad energimerking hvor det står en issuedDate og en expireDate til en rad per måned i dette intervallet. 
    # Koden går først gjennom alle rader med energimerkinger. Deretter sjekker den om issuedDate(startdato) er null. Da vil vi ikke ha noen mulighet til å lage et intervall, og vi legger raden helt sånn som den er. Kolonna first_date_in_month vil være null i disse tilfellene, så man kan feilsøke på det. Det burde her også opprettes en alert som sier ifra i disse tilfellene.
    # Deretter sjekker koden om expireDate er null. Dersom den er det antar vi at energimerkingen er gyldig i 12 mnd. Det er ikke videre diskutert om dette er en gyldig antakelse. Her burde vi også utløse en alert.
    # Nå vet vi at vi har både en gyldig startdato og en gyldig sluttdato. Siden vi ønsker at alle måneder skal bli identifisert av sin first_date_in_month setter vi loopens første dato til den første dagen i den måneden issuedDate er i. Dersom energimerkingen ble utstedt den 18/08/2016 vil den første raden få first_date_in_month=01/08/2016.
    # Deretter har vi en loop som for hver måned setter kolonnen first_date_in_month og legger raden til arrayet data[]. Dette blir senere skrevet som Delta til sølv.

    data = []

    for index, row in silver_pd_df.iterrows():
    
        if not row[start_date_column_in_input_table]:
            print("start date is null")
            data.append(deepcopy(row))
            continue
            # TODO Implement alert if issuedDate is null

        if not row[end_date_column_in_input_table]:
            loop_end_date = loop_starting_date + relativedelta(months=12) - timedelta(days=1)
            # TODO Implement alert if expireDate is null

        loop_starting_date = row[start_date_column_in_input_table] - timedelta(days=row[start_date_column_in_input_table].day-1)
        loop_end_date = row[end_date_column_in_input_table]

        for dt in rrule.rrule(rrule.MONTHLY, dtstart=loop_starting_date, until=loop_end_date):
            row[date_column_in_output_table] = dt.date()
            data.append(deepcopy(row))


    # Forklaring av koden under:
    # Koden er implementert for å håndtere de tilfeller hvor en gyldigheten til en energimerking er ferdig og en ny begynner, for samme eiendom.
    # Eksempel: En eiendom har en energimerking som er gyldig fra 18/08/2016 til 19/09/2016, og en annen energimerking som er gyldig fra 19/09/2016 til 19/09/2026. I September 2016 vil det da i utgangspunktet være 2 rader for den aktuelle eiendommen, noe vi ikke ønsker. Koden over regner ut hvor mange dager hver av energimerkingen har i gjeldene måned, og velger den energimerkingen som har flest dager. I dette eksemplet har den første energimerkingen 19 dager av September 2016, mens den andre har de resterende 11 dagene. Derfor vil den første energimerkingen være gjeldene for September 2016.
    # Koden sammenlikner alle rader i datasettet med seg selv, hhv. row_i og row_j. Vi vil luke ut de tilfellene hvor starttidspunktet til en energimerking er lik som sluttidspunktet på en annen.
    # Vi starter med å for hver rad i sjekke om den aktuelle måneden vi er på er den siste gyldige måneden i energimerkingen(samme måned som expireDate.) Grunnen til at vi sammenlikner med first_date_in_month er at vi tidligere gjør om alle måneder til first_date_in_month. Fra eksemplet over vil derfor både den første og den andre energimerkingen ha 01/09/2016 på sin kolonne first_date_in_month for måned september 2016.
    # Deretter sammenlikner vi denne siste gyldige måneden med alle andre energimerkinger. Hvis vi finner en annen energimerking på samme eiendom som starter i samme måned som denne slutter, regner vi ut hvilken av de to energimerkingene som ar flest dager. Deretter sletter vi den raden som har færrest dager.

    # The code beneath fixes overlapping certifications
    # LOGIC: The certification with the most days in the given month "gets" the month

    for i, row_i in enumerate(data):
        if row_i[end_date_column_in_input_table] - timedelta(days=row_i[end_date_column_in_input_table].day-1) == row_i[date_column_in_output_table]:
            for j, row_j in enumerate(data):
                # Skip comparing the row with itself
                if i == j:
                    continue
                if row_j[start_date_column_in_input_table] - timedelta(days=row_j[start_date_column_in_input_table].day-1) == row_j[date_column_in_output_table] and row_i[end_date_column_in_input_table] == row_j[start_date_column_in_input_table] and row_i[business_key_in_input_table] == row_j[business_key_in_input_table]:
                    if row_i[end_date_column_in_input_table].day > ((row_j[start_date_column_in_input_table]+MonthEnd(0)).day-row_j[start_date_column_in_input_table].day):
                        #i has most days -> delete j
                        del data[j]
                    else:
                        del data[i]


    new_pd_df = pd.DataFrame(data)
    new_spark_df = spark.createDataFrame(new_pd_df)

    new_spark_df.write.format("delta").mode("overwrite").save(full_new_silver_path)