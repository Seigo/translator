import pandas as pd
import json

path_to_input_files = "./test_input_files"
USAGE_REPORT_FILEPATH = f'{path_to_input_files}/Sample_Report.csv'
PARTNER_TO_PRODUCT_MAP_FILEPATH = f'{path_to_input_files}/typemap.json'

PARTNER_IDS_TO_SKIP = [26392]

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
        # 'itemname', 'plan', 'itemType', 
        'PartNumber', 'itemCount'
    ]]

    # ### ============== COMMON between Chargeable and Domains ============== ###
    # Map 'accountGuid' to 'partnerPurchasedPlanID' as alphanumeric string of length 32 and should strip any non-alphanumeric characters before insert.
    # - Sample: 799ef0ab-4438-4157-8afc-f6fc4dfe9253
    # - Keep only alphanumeric characters
    # - If length is not equal to 32: throw error? Or log error and skip that row? Throwing error for now
    def mapToAlphanum(input_str):
        # TODO: consider refactoring to use regex?
        result = ""
        for char in input_str:
            if char.isalnum():
                result = result + char
        # make sure the string has length 32
        if len(result) != 32:
            raise Exception('Every partnerPurchasedPlanID should have 32 characters. Found: ' + result)
        return result
    df['partnerPurchasedPlanID'] = df['accountGuid'].map(mapToAlphanum)
    print(df.head(5));

    # ### ============== CHARGEABLE ============== ###
    # Log an error and skip entries: without 'PartNumber'
    # Log an error and skip entries: with non-positive 'itemCount'
    # Skip any entries where the value of PartnerID matches a configurable list of 'PartnerID' [Note:  for the purpose of this exercise the list of PartnerIDs to skip contains just 26392]
    # Map 'PartNumber' in the csv to the 'product' column in the 'chargeable' table based on the map in the attached typemap.json file. For example the PartNumber ADS000010U0R will be mapped to product value 'core.chargeable.adsync' for the insert.
    # - Load `typemap.json`
    with open(PARTNER_TO_PRODUCT_MAP_FILEPATH, 'r') as f:
        partner_to_product_map = json.load(f)
        # TODO: handle error if there's any failure in loading the JSON file
    # - Map 'PartNumber' in the csv to the 'product' column (e.g: PartNumber 'ADS000010U0R' to product 'core.chargeable.adsync')
    
    # Map 'itemCount' in csv as 'usage' in the table subject to a unit reduction rule 
    # Output stats of running totals over 'itemCount' for each of the products in a success log
    # Bonus: validate and escape inputs to secure against SQL injection
    # Prepare SQL inserts for `chargeable` table
        # id: int auto-increment	
        # partnerID: int	
        # product: varchar
        # partnerPurchasedPlanID: varchar
        # plan: varchar
        # usage: int

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
