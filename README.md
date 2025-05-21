# Usage Translator

This project generates two SQL files with an `INSERT` statement for the `chargeable` and `domains` tables.

It requires an input of two files: "Usage Report" CSV and a "Product Typemap" JSON

The generated SQL is not executed in this project, it is expected to be reviewed/executed manually or in other systems.

All string values are escaped to prevent SQL injection: single quotes (') are replaced with two single quotes ('')

---

## ✨ Features

- Reads a usage report CSV and a product typemap JSON.
- Outputs SQL `INSERT` statements for normalized tables (Chargeable & Domain).
- Escapes all string values to prevent SQL injection.
- Logs errors and skips invalid entries.
- Outputs error and stats CSVs for auditing.
- Easily configurable via `.env` file.

---

## 📦 Requirements

- Python 3.10+
- [pandas](https://pandas.pydata.org/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## ⚙️ Project Setup

1. **Clone the repository and enter the folder:**

   ```shell
   git clone https://github.com/Seigo/translator
   cd translator
   ```

2. **Create and activate a virtual environment:**

   ```shell
   python3 -m venv .venv
   # On Linux/Mac:
   source .venv/bin/activate
   # On Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```shell
   pip install -r requirements.txt
   ```

4. **Configure your `.env` file:**

   Rename `.env.example` to `.env` : `cp ./.env.example ./.env` OR, create an `.env` file containing:

   ```
   OUTPUT_FILES_PATH=./output
   PARTNUMBER_TO_PRODUCT_MAP_FILEPATH=./input/product_type_mapping.json
   USAGE_REPORT_FILEPATH=./input/sample_usage_report.csv
   PARTNER_IDS_TO_SKIP=26392
   HEADERS=PartnerID,accountGuid,domains,plan,PartNumber,itemCount
   ITEMCOUNT_TO_USAGE_REDUCTION_RULES={"EA000001GB0O": 1000, "PMQ00005GB0R": 5000, "SSX006NR": 1000,"SPQ00001MB0R": 2000}
   ```

5. **Place your input files:**

   For this exercise, this repo already includes the input files, so you don't need to do anything

   But, if you want to update them, put them in `input` folder and rename accordingly:

   ```
   input/
   ├─ sample_usage_report.csv
   └─ product_type_mapping.json
   ```

---

## 🚀 Running the Project

```shell
python run.py
```

The output files will be written to the folder specified in your `.env` (default: `output/`):

```
output/
├─ insert_into_chargeable.sql
├─ insert_into_domains.sql
├─ itemcount_nonpositive_error_df.csv
├─ no_partnumber_error_df.csv
├─ running_totals_df.csv
```

---

## 🧪 Running Tests

All tests are located in the `tests/` folder.

```shell
pytest -v
```

---

## 📝 Example Inputs

### Usage Report CSV

```csv
PartnerID,partnerGuid,accountid,accountGuid,username,domains,itemname,plan,itemType,PartNumber,itemCount
26392,f72f467d-da62-47c7-b063-0301cdc58e43,1561965,799ef0ab-4438-4157-8afc-f6fc4dfe9253,HW-Acceptance,HW-Acceptance.serverdata.net,Account_contacts,E2016_Exch_1_HOSTWAY,0,,3
26392,f72f467d-da62-47c7-b063-0301cdc58e43,1561965,799ef0ab-4438-4157-8afc-f6fc4dfe9253,HW-Acceptance,HW-Acceptance.serverdata.net,Account_contacts,E2016_Exch_1_HOSTWAY,0,AC0000010U0R,4
26392,f72f467d-da62-47c7-b063-0301cdc58e43,1561965,799ef0ab-4438-4157-8afc-f6fc4dfe9253,HW-Acceptance,HW-Acceptance.serverdata.net,ActiveSync_mailboxes,E2016_Exch_1_HOSTWAY,0,,3
```

### Product Typemap JSON

```json
{
  "ADS000010U0R": "core.chargeable.adsync",
  "SSX00010GB0R": "core.chargeable.sharesync10gb",
  "CD000001SU0R": "core.chargeable.comdisclaimsvcs"
}
```

---

## 🏁 Example Output

### Chargeable Table

```sql
INSERT INTO chargeable ("partnerID", "product", "partnerPurchasedPlanID", "plan", "usage") VALUES
(26668, 'core.chargeable.exchange', 'ff633524c35f4de8acdaa7cdee38cd15', 'E2016_Exch_1_HOSTWAY', 2),
(26668, 'core.chargeable.advancemailsec', 'ff633524c35f4de8acdaa7cdee38cd15', 'E2016_Exch_1_HOSTWAY', 2),
(26668, 'core.chargeable.owa', '6a1e663c829e4e79ac16fca89d61f143', 'E2016_Exch_1_HOSTWAY', 2);
```

### Domains Table

```sql
INSERT INTO domains ("partnerPurchasedPlanID", "domain") VALUES
('799ef0ab443841578afcf6fc4dfe9253', 'HW-Acceptance.serverdata.net'),
('fcf200b3b7e4494dbe6f93c8243ba3c6', 'MigrationTest.serverdata.net'),
('85c57a080ddd4d30beaf48ff81355b2f', 'georgi660336.serverdata.net');
```

---

## 🛡️ Security

- All string values are escaped to prevent SQL injection (single quotes are doubled).
- Only valid and sanitized data is included in the output.

---
