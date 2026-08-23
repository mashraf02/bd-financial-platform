import openpyxl

path = "data/raw/bangladesh_bank/2026/08/23/time_series_data1972-2024.xlsx"
wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
ws = wb["Table IB"]

for i, row in enumerate(ws.iter_rows(values_only=True)):
    print(row)
    if i > 15:
        break
