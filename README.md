# Translator

This project generates two SQL files with an `INSERT` statement for the `chargeable` and `domains` tables

It requires an input of two files: "Usage Report" CSV and a "Product Typemap" JSON

The generated SQL is not executed in this project, it is expected to be reviewed/executed manually or in other systems.

All string values are escaped to prevent SQL injection: single quotes (') are replaced with two single quotes ('')

## Example input: Usage Report CSV

```
PartnerID,partnerGuid,accountid,accountGuid,username,domains,itemname,plan,itemType,PartNumber,itemCount
26392,f72f467d-da62-47c7-b063-0301cdc58e43,1561965,799ef0ab-4438-4157-8afc-f6fc4dfe9253,HW-Acceptance,HW-Acceptance.serverdata.net,Account_contacts,E2016_Exch_1_HOSTWAY,0,,3
26392,f72f467d-da62-47c7-b063-0301cdc58e43,1561965,799ef0ab-4438-4157-8afc-f6fc4dfe9253,HW-Acceptance,HW-Acceptance.serverdata.net,Account_contacts,E2016_Exch_1_HOSTWAY,0,AC0000010U0R,4
26392,f72f467d-da62-47c7-b063-0301cdc58e43,1561965,799ef0ab-4438-4157-8afc-f6fc4dfe9253,HW-Acceptance,HW-Acceptance.serverdata.net,ActiveSync_mailboxes,E2016_Exch_1_HOSTWAY,0,,3
```

## Example input: Product Typemap JSON

```
{
  "ADS000010U0R": "core.chargeable.adsync",
  "SSX00010GB0R": "core.chargeable.sharesync10gb",
  "CD000001SU0R": "core.chargeable.comdisclaimsvcs",
}
```

## Example output

For the `chargeable` table:

```
INSERT INTO chargeable ("partnerID", "product", "partnerPurchasedPlanID", "plan", "usage") VALUES
(26668, 'core.chargeable.exchange', 'ff633524c35f4de8acdaa7cdee38cd15', 'E2016_Exch_1_HOSTWAY', 2),
(26668, 'core.chargeable.advancemailsec', 'ff633524c35f4de8acdaa7cdee38cd15', 'E2016_Exch_1_HOSTWAY', 2),
(26668, 'core.chargeable.owa', '6a1e663c829e4e79ac16fca89d61f143', 'E2016_Exch_1_HOSTWAY', 2)
;
```

For the `domains` table:

```
INSERT INTO domains ("partnerPurchasedPlanID", "domain") VALUES
('799ef0ab443841578afcf6fc4dfe9253', 'HW-Acceptance.serverdata.net'),
('fcf200b3b7e4494dbe6f93c8243ba3c6', 'MigrationTest.serverdata.net'),
('85c57a080ddd4d30beaf48ff81355b2f', 'georgi660336.serverdata.net')
;
```

## Requirements

- Python 3.13.0
- pandas

## Project Setup

On your terminal

```shell
python3 -m venv .venv
source .venv/bin/activate

pip install .
```

## Run project

Place the input files on the folder `input_files`:

```
input_files
├─ Sample_Report.csv
├─ typemap.json
```

Run with

```shell
python main.py
```

Then, the output files will be writen to the `output_files` folder:

```
output_files
├─ insert_into_chargeable.sql
├─ insert_into_domains.sql
├─ itemcount_negative_error_df.csv
├─ no_partnumber_error_df.csv
├─ running_totals_df.csv
```

## TODO: (optional) Test with local DB

On your terminal, setup local test DB

```shell
# TODO: docker compose
# TODO: how to setup `chargeable` and `domains` table
```
