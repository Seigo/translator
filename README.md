# Translator

This project generates two SQL files with an `INSERT` statement for the `chargeable` and `domains` tables.

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

## Notes

- [x] Complexity analysis: see branch `complexity_analysis`
- Consider the complexity of doing a lot of Dataframe filtering versus making one big loop that processes every logic for each row
- [ ] what are the risks when the data types are being defined when receiving the CSV input?
- Do deeper research on DF filtering (e.g: `df[df['my_column'].notna()]`) for time and space complexity
- Git commits

  - Commits were made very short, in order to be easir to read. In a real project, we would git-squash the commits in the PR, and rebase it on the newest version of the `dev` branch. That way we get a very clean git history
  - Commits in the "middle" of the branch included lots of prints for debugging, in order to ilustrate the development process

- [x] Escape SQL inserts to prevent SQL injection attacks
  - Given this SO answer: https://stackoverflow.com/questions/71604741/sql-sanitize-python
    - Consider moving the responsibility to the part that executes the SQL, and make sure it is always using escaped parameter passing
      - [x] But assuming we can't do that, we should escape the strings before saving to file. Then we assume that the file will be correctly executed with the escaped strings
- [ ] Add validation for all input fields
  - null
  - out of bounds
  - file type
  - Consider File size limits for input
  - unsupported characters
  - character encoding
- [ ] Add Linter
- [x] When generating running totals over 'itemCount', should this table be ordered in a specific way to make more sense of the running totals?
  - Maybe not, because maybe they wanted the "running totals" to be a sum of itemCounts grouped by product
    - Previous implementation:
      - #running_totals_df['running_total'] = running_totals_df['itemCount'].cumsum()
      - #running_totals_df.to_csv(f'{OUTPUT_FILES_PATH}/running_totals_df.csv', index=False)
- [x] The error logs are CSV's with rows that have a specific error. They were generated with `.copy(deep=True)` to prevent filtering in any DF to not interfere with another. In order to save memory space, we could move up the CSV generation to be made as soon as possible, and then assign `None` to the DF error log variable (since it could be a quite large object)
- [ ] Consider kinds of systems design architecture
  - Consider kinds of deployment
    - AWS S3, queues, Lambdas
      - These input files would come from somewhere, maybe a queue? (files uploaded to S3, and the event and filenames are sent to RabbitMQ)
      - This process looks like something you would want to be ran everyday at a certain time after the other parties had the time to process and submit to you. Since we wouldn't need a service to be listening 24/7, we can use Lambda for file upload
      - The output files can also be stored on S3, and its executing triggered by the end of the previous processing. Saving output files could be very useful in case of bugs, monitoring or even auditing
      - Any exceptions during processing should send an event on an alerting system
- [ ] Consider adding idempotency to the SQL output files (running with the same inputs wouldn't cause duplicate entries on the DB)
