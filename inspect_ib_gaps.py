import pandas as pd

path = "data/raw/bangladesh_bank/2026/08/23/time_series_data1972-2024.xlsx"
df = pd.read_excel(path, sheet_name="Table IB", header=None, skiprows=9)

for _, row in df.iterrows():
    period = row[0]
    if isinstance(period, str) and "-" in period:
        print(f"{period!r}  col27={row[27]!r}  col28={row[28]!r}  col31={row[31]!r}  col32={row[32]!r}")
