import pandas as pd

path_to_input_files = "./test_input_files"

# Use Pandas to read the Sample Report CSV
df = pd.read_csv(f'{path_to_input_files}/Sample_Report.csv')
print(df.head(5));

print('Initializing the Translator')


