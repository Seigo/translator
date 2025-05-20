import pandas as pd
import json

INPUT_FILES_PATH = "./test_input_files"
USAGE_REPORT_FILEPATH = f'{INPUT_FILES_PATH}/Sample_Report.csv'
PARTNUMBER_TO_PRODUCT_MAP_FILEPATH = f'{INPUT_FILES_PATH}/typemap.json'

OUTPUT_FILES_PATH = "./test_output_files"

# TODO: lookup best practices on environment variables or similar
PARTNER_IDS_TO_SKIP = [26392]

ITEMCOUNT_TO_USAGE_REDUCTION_RULES = {
    'EA000001GB0O': 1000,
    'PMQ00005GB0R': 5000,
    'SSX006NR': 1000,
    'SPQ00001MB0R': 2000
}

# Dummy error logger
error_logs = []
def log_error(error_string):
    error_logs.append(error_string)

print('Initializing the Translator')

def prepare_inserts(usage_report_filepath):
    # Read Sample Report CSV
    df = pd.read_csv(usage_report_filepath)

    # Filter out unnecessary columns to work with smaller dataframe
    df = df[[
        'PartnerID', 
        # 'partnerGuid', 'accountid', 
        'accountGuid', 
        # 'username',
       'domains', 
        # 'itemname', 
        'plan',
        # 'itemType', 
        'PartNumber', 'itemCount'
    ]].copy()

    # ### ============== COMMON between Chargeable and Domains ============== ###
    # Map 'accountGuid' to 'partnerPurchasedPlanID' as alphanumeric string of length 32 and should strip any non-alphanumeric characters before insert.
    # - Sample: 799ef0ab-4438-4157-8afc-f6fc4dfe9253
    # - Keep only alphanumeric characters
    # - If length is not equal to 32: throw error? Or log error and skip that row? Throwing error for now
    def map_to_alphanum(input_str):
        # TODO: consider refactoring to use regex?
        result = ""
        for char in input_str:
            if char.isalnum():
                result = result + char
        # make sure the string has length 32
        if len(result) != 32:
            raise Exception('Every partnerPurchasedPlanID should have 32 characters. Found: ' + result)
        return result
    df['partnerPurchasedPlanID'] = df['accountGuid'].map(map_to_alphanum)

    # ### ============== CHARGEABLE ============== ###
    # Create a copy of the dataframe to apply filters only for `chargeable` table
    chargeable_df = df.copy()
    print(len(df), len(chargeable_df))
    
    # df: 13424
    # chargeable_df: 13424

    # Log an error and skip entries: without 'PartNumber'
    # - TODO: add tests to verify that it catches: empty column, Null, None, other types, out of bounds
    no_partnumber_error_df = chargeable_df[chargeable_df['PartNumber'].isna()]
    chargeable_df = chargeable_df[chargeable_df['PartNumber'].notna()]

    # chargeable_df: 4010

    # Log an error and skip entries: with non-positive 'itemCount'
    itemcount_negative_error_df = chargeable_df[chargeable_df['itemCount'] < 0]
    chargeable_df = chargeable_df[chargeable_df['itemCount'] >= 0]

    # chargeable_df: 4008

    # Skip any entries where the value of PartnerID matches a configurable list of 'PartnerID' [Note:  for the purpose of this exercise the list of PartnerIDs to skip contains just 26392]
    chargeable_df = chargeable_df[~chargeable_df['PartnerID'].isin(PARTNER_IDS_TO_SKIP)]

    # chargeable_df: 3909

    # Map 'PartNumber' in the csv to the 'product' column in the 'chargeable' table based on the map in the attached typemap.json file. For example the PartNumber ADS000010U0R will be mapped to product value 'core.chargeable.adsync' for the insert.
    # - Load `typemap.json`
    with open(PARTNUMBER_TO_PRODUCT_MAP_FILEPATH, 'r') as f:
        partnumber_to_product_map = json.load(f)
        # TODO: handle error if there's any failure in loading the JSON file
    assert type(partnumber_to_product_map) is dict, "PARTNUMBER_TO_PRODUCT_MAP_FILEPATH is not a dictionary"
    # - Map 'PartNumber' in the csv to the 'product' column (e.g: PartNumber 'ADS000010U0R' to product 'core.chargeable.adsync')
    chargeable_df['product'] = chargeable_df['PartNumber'].map(partnumber_to_product_map)

    # chargeable_df: 3909

    # Map 'itemCount' in csv as 'usage' in the table subject to a unit reduction rule 
    assert type(ITEMCOUNT_TO_USAGE_REDUCTION_RULES) is dict, "ITEMCOUNT_TO_USAGE_REDUCTION_RULES is not a dictionary"
    def map_itemcount_to_usage(row): 
        result = row['itemCount']
        key = row['PartNumber']
        if key in ITEMCOUNT_TO_USAGE_REDUCTION_RULES:
            result = result / ITEMCOUNT_TO_USAGE_REDUCTION_RULES[key]
        return result
    chargeable_df['usage'] = chargeable_df.apply(map_itemcount_to_usage, axis=1)

    # chargeable_df: 3909

    # TODO Bonus: validate and escape inputs to secure against SQL injection
    # Output stats of running totals over 'itemCount' for each of the products in a success log
    running_totals_df = chargeable_df[[
        'product', 'itemCount'
    ]].copy()
    running_totals_df['running_total'] = running_totals_df['itemCount'].cumsum()

    # chargeable_df: 3909

    # Debug:
    print(len(df), len(chargeable_df), len(no_partnumber_error_df), len(itemcount_negative_error_df), len(running_totals_df))
    df.to_csv(f'{OUTPUT_FILES_PATH}/df.csv')
    chargeable_df.to_csv(f'{OUTPUT_FILES_PATH}/chargeable_df.csv')
    no_partnumber_error_df.to_csv(f'{OUTPUT_FILES_PATH}/no_partnumber_error_df.csv')
    itemcount_negative_error_df.to_csv(f'{OUTPUT_FILES_PATH}/itemcount_negative_error_df.csv')
    running_totals_df.to_csv(f'{OUTPUT_FILES_PATH}/running_totals_df.csv')
    
    # Prepare SQL inserts for `chargeable` table
        # id: int auto-increment	
        # partnerID: int	
        # product: varchar
        # partnerPurchasedPlanID: varchar
        # plan: varchar
        # usage: int
    with open(f'{OUTPUT_FILES_PATH}/insert_into_chargeable.sql', "w") as f:
        start_of_query = 'INSERT INTO chargeable ("partnerID", "product", "partnerPurchasedPlanID", "plan", "usage") VALUES'
        row_array = []
        for _, row in chargeable_df.iterrows():
            usage = int(row['usage']) # TODO: int() does a floor function, is that what we want?
            # TODO: escape strings to prevent SQL injection (see more: https://stackoverflow.com/questions/71604741/sql-sanitize-python)
            row_query = f"({row['PartnerID']}, '{row['product']}', '{row['partnerPurchasedPlanID']}', '{row['plan']}', {usage})"
            row_array.append(row_query)

        f.write(start_of_query + '\n')
        f.write(',\n'.join(row_array) + '\n')
        f.write(';\n') # end_of_query

    # ### ============== DOMAINS ============== ###
    # Record the Domain associated with the partnerPurchasedPlanID in the table
    # Ensure only distinct domain names are recorded in the 'domains' table
    # Bonus: validate and escape inputs to secure against SQL injection
    # Prepare SQL inserts for `domains` table
        # id: int auto-increment
        # partnerPurchasedPlanID: varchar
        # domain: varchar

inserts = prepare_inserts(USAGE_REPORT_FILEPATH)
# Write `inserts` to an output file
