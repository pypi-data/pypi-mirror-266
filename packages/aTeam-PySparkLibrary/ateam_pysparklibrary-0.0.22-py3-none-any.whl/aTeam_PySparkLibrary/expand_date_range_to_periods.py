#### Kontaktperson: Ludvig Løite
#### Denne er veldig spesifikk for contract lines. Krever en del å spesialtilpasse for andre tabeller.



from pyspark.sql.functions import lit,  col
import pandas as pd
from pandas.tseries.offsets import MonthEnd
from datetime import timedelta, date
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from copy import deepcopy



storage_account_name = "pedataplatformdev"
silver_fact_contract_lines_path = "Facts/ContractLines"
new_silver_fact_contract_lines_path = "Facts/MonthlyContractLines"

def expand_date_range_to_periods(storage_account_name, silver_fact_contract_lines_path, new_silver_fact_contract_lines_path, silver_dim_contract_path, spark):
   

    full_silver_path = f"abfss://silver@{storage_account_name}.dfs.core.windows.net/{silver_fact_contract_lines_path}/"
    full_new_silver_path = f"abfss://silver@{storage_account_name}.dfs.core.windows.net/{new_silver_fact_contract_lines_path}/"
    full_dim_contract_path = f"abfss://silver@{storage_account_name}.dfs.core.windows.net/{silver_dim_contract_path}/"


    silver_df = spark.read.format("delta").load(full_silver_path)
    silver_df_new = silver_df.withColumn("invoice_date", lit(None))
    silver_df_new = silver_df_new.withColumn("invoice_price", lit(None))

    silver_pd_df = silver_df_new.toPandas()
    contract_df = spark.read.format("delta").load(full_dim_contract_path)


    def findLoopEndDate(contract_row):
        # Henter status på kontraktslinja fra kontrakten(som ligger en abstraksjon/nivå opp)
        contract_line_status = contract_df.filter(col('pk_dim_contract_key') == contract_row['fk_dim_contract_key']).select("contract_status").collect()[0]["contract_status"]
        
        # Hvis kontrakten er aktiv setter vi sluttdato mellom 12 og 13 måneder frem i tid.
        if contract_line_status == 'ACTIVE':
            loop_end_date = date.today() + relativedelta(months=12) + MonthEnd(0)
        
        # Hvis kontrakten ikke er aktiv bruker vi kolonnen next_invoice_date og setter varigheten til et antall måneder etter dette basert på 'frequency' 
        else:
            invoice_frequency = contract_row['frequency']
            next_invoice_date = contract_row["next_invoice_date"]

            if invoice_frequency == 'MONTHLY':
                loop_end_date = next_invoice_date + relativedelta(months=1) - timedelta(days=1)
            elif invoice_frequency == 'QUARTERLY':
                loop_end_date = next_invoice_date + relativedelta(months=3) - timedelta(days=1)
            elif invoice_frequency == 'YEARLY':
                loop_end_date = next_invoice_date + relativedelta(months=12) - timedelta(days=1)
            else:
                print('Invoice frequency unknown')
                loop_end_date = -1
            #print(invoice_frequency,", next_invoice: ", next_invoice_date,", calculated_end_date: ", loop_end_date)
        return loop_end_date


    data = []

    debugIndex = 0
    noEndDateIndex = 0
    noStartDateIndex = 0
    totalPriceIsZero = 0

    debugContracts = [-1, 23213]
    debugSpecificContract = debugContracts[1]


    # Går gjennom alle kontraktslinjer. 
    # Målet er å få kontraktslinjene til en rad per måned. For hver av disse radene legger vi inn verdier til kolonnene 'invoice_date' og 'invoice_price'
    # Problemet er at mange kontraktslinjer ikke starter og slutter på hele måneder. Noen rader har heller ikke sluttdato. 


    for _, row in silver_pd_df.iterrows():
        
        # total_price er årlig leiepris
        monthly_price = float(row['total_price'])/12

        loop_starting_date = row['start_date']
        loop_end_date = row['end_date']

        # For debugging
        if row['total_price'] == 0:
            totalPriceIsZero += 1
            
        # Hvis start_date er null har vi et problem. Det er ingen tilfeller av dette i datasettet    
        if not row['start_date']:
            print("start date is null")
            noStartDateIndex += 1
            debugIndex += 1
            data.append(deepcopy(row))
            continue

        # Hvis startdatoen ikke er første dag i måneden, må vi regne ut leieprisen for denne måneden, basert på hvor mange dager det er igjen av måneden.
        if row['start_date'].day != 1:
            lastDayOfMonth = row['start_date'] + MonthEnd(0)

            # Legger til 1 siden leietaker også betaler for hele start_date
            numberOfPayableDays = lastDayOfMonth.day - row['start_date'].day + 1

            # Leieprisen er antall dager igjen av måneden delt på hvor mange dager totalt det er i måneden, ganget med månedlig leiepris.
            first_invoice_price = monthly_price*numberOfPayableDays/lastDayOfMonth.day

            # Legger til denne nye raden i 'data'
            row['invoice_date'] = row['start_date']
            row['invoice_price'] = first_invoice_price
            data.append(deepcopy(row))

            # Setter "hovedloopen" til å starte på første dagen i ny måned
            loop_starting_date = lastDayOfMonth + timedelta(days=1)

            if row['contract_line_id'] == debugSpecificContract:
                print("Start date: ", row['start_date'])
                print("Added row: invoice_date: ", row['invoice_date']," invoice_price: ", row['invoice_price'])
                print("New loop_starting_date set: ", loop_starting_date)

        # Hvis kontrakten ikke har en end_date, har vi laget en logikk for å bestemme sluttdato. I Power BI-dashboardet kan man se kontraktsleie 12 mnd frem i tid, og vi ønsker å ha midlertidige kontrakter(uten sluttdato) i denne oversikten.
        if not row['end_date']:
            loop_end_date = findLoopEndDate(row)
            noEndDateIndex+=1

        # Hvis sluttdato ikke er siste dag i en måned, må vi regne ut leieprisen for denne måneden, basert på hvor mange dager det er igjen av måneden.
        if pd.Timestamp(loop_end_date) != loop_end_date + MonthEnd(0):
            numberOfPayableDays = loop_end_date.day

            # Leieprisen er antall dager igjen av måneden delt på hvor mange dager totalt det er i måneden, ganget med månedlig leiepris.
            last_invoice_price = monthly_price*numberOfPayableDays/(loop_end_date + MonthEnd(0)).day
            
            # Legger til den siste raden i 'data'
            row['invoice_date'] = loop_end_date - timedelta(days=loop_end_date.day-1)
            row['invoice_price'] = last_invoice_price
            data.append(deepcopy(row))

            # Setter "hovedloopen" til å slutte på siste dag i måneden før
            loop_end_date = loop_end_date - timedelta(days=loop_end_date.day)

            if row['contract_line_id'] == debugSpecificContract:
                print("End date: ", row['end_date'])
                print("Added row: invoice_date: ", row['invoice_date']," invoice_price: ", row['invoice_price'])
                print("New loop_end_date set: ", loop_end_date)


        # Vi har nå en loop_starting_date som alltid er første dagen i en måned og en loop_end_date som alltid er siste dagen i en måned. 
        # Vi går gjennom alle måneder mellom disse datoene og lager en ny rad pr
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=loop_starting_date, until=loop_end_date):
            row['invoice_date'] = dt.date()
            row['invoice_price'] = monthly_price
            data.append(deepcopy(row))
            if row['contract_line_id'] == debugSpecificContract:
                print("Added row: invoice_date: ", row['invoice_date']," invoice_price: ", row['invoice_price'])
        
        debugIndex+=1

    print("end_date is null for ", noEndDateIndex, " contract lines")
    print("start_date is null for ", noStartDateIndex, " contract lines")
    print("total_price is zero for ",totalPriceIsZero, " contract lines")
    print("Total contract lines: ", debugIndex)


    # In[30]:


    new_pd_df = pd.DataFrame(data)
    new_spark_df = spark.createDataFrame(new_pd_df)

    new_spark_df = new_spark_df.withColumn("area_group_name", col("area_group_name").cast("string"))

    new_spark_df.printSchema()

    #new_spark_df.write.format("delta").mode("overwrite").save(full_new_silver_path)


    # Så når jeg gikk gjennom at koden her ikke vil bli riktig hvis en kontrakt starter og slutter i samme måned.
    # 
    # 
    # Problem 2: Vi regner nå prisen for x antall dager basert på hvor mange dager det er i den gjeldende måneden. Det vil si at en dag i februar koster med enn en dag i mars. En annen mulighet er å ta totalpris / 365 og så gange opp prisen hver måned. Leiepris pr mnd vil da bli ulik. Dette er også ikke regnskapsdato men et predikat på leieinntekter basert på kontrakter. Til dette virker det bra.
