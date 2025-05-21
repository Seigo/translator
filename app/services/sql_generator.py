import pandas as pd
from typing import Any
from app.utils.strings import escape_sql_value

class SQLGenerator:
    @classmethod
    def write_chargeable_sql(cls, chargeable_df: pd.DataFrame, output_files_path: str) -> None:
        """Write SQL insert statements for the chargeable table."""
        with open(f'{output_files_path}/insert_into_chargeable.sql', "w") as f:
            columns = ["partnerID", "product", "partnerPurchasedPlanID", "plan", "usage"]
            columns = list(map(lambda c: f'"{c}"', columns))
            start_of_query = f'INSERT INTO chargeable ({", ".join(columns)}) VALUES'
            row_array = []
            for _, row in chargeable_df.iterrows():
                usage = int(row['usage'])
                values = [row['PartnerID'], row['product'], row['partnerPurchasedPlanID'], row['plan'], usage]
                values = list(map(escape_sql_value, values))
                row_query = f"({', '.join(values)})"
                row_array.append(row_query)
            f.write(start_of_query + '\n')
            f.write(',\n'.join(row_array) + '\n')
            f.write(';\n')

    @classmethod
    def write_domains_sql(cls, domains_df: pd.DataFrame, output_files_path: str) -> None:
        """Write SQL insert statements for the domains table."""
        with open(f'{output_files_path}/insert_into_domains.sql', "w") as f:
            columns = ['partnerPurchasedPlanID', 'domain']
            prepared_columns = list(map(lambda c: f'"{c}"', columns))
            start_of_query = f'INSERT INTO domains ({", ".join(prepared_columns)}) VALUES'
            row_array = []
            for _, row in domains_df.iterrows():
                values = [row['partnerPurchasedPlanID'], row['domains']]
                prepared_values = list(map(escape_sql_value, values))
                row_query = f"({', '.join(prepared_values)})"
                row_array.append(row_query)
            f.write(start_of_query + '\n')
            f.write(',\n'.join(row_array) + '\n')
            f.write(';\n')