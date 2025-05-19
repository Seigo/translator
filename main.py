import pandas as pd

path_to_input_files = "./test_input_files"
USAGE_REPORT_FILEPATH = f'{path_to_input_files}/Sample_Report.csv'

# Dummy error logger
error_logs = []
def log_error(error_string):
    error_logs.append(error_string)

print('Initializing the Translator')

def prepare_chargeable_inserts(usage_report_filepath):
    # Read Sample Report CSV
    df = pd.read_csv(usage_report_filepath)

    # Filter out unnecessary columns to work with smaller dataframe
    print(df.columns)
    df = df[[
        'PartnerID', 
        # 'partnerGuid', 'accountid', 
        'accountGuid', 
        # 'username',
       'domains', 
        # 'itemname', 'plan', 'itemType', 
        'PartNumber', 'itemCount'
    ]]
    print(df.head(5));

    # Log an error and skip entries: without ‘PartNumber’
    # Log an error and skip entries: with non-positive ‘itemCount’
    # Skip any entries where the value of PartnerID matches a configurable list of ‘PartnerID’ [Note:  for the purpose of this exercise the list of PartnerIDs to skip contains just 26392]
    # Map ‘PartNumber’ in the csv to the ‘product’ column in the ‘chargeable’ table based on the map in the attached typemap.json file. For example the PartNumber ADS000010U0R will be mapped to product value ‘core.chargeable.adsync’ for the insert.
    # Map ‘accountGuid’ to ‘partnerPurchasedPlanID’ as alphanumeric string of length 32 and should strip any non-alphanumeric characters before insert.
    # Map ‘itemCount’ in csv as ‘usage’ in the table subject to a unit reduction rule 
    # Output stats of running totals over ‘itemCount’ for each of the products in a success log
    # Bonus: validate and escape inputs to secure against SQL injection
    # Prepare SQL inserts for `chargeable` table

chargeable_inserts = prepare_chargeable_inserts(USAGE_REPORT_FILEPATH)
# Write `chargeable_inserts` to an output file