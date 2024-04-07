import pandas as pd


def read_excel(file_name, sheet_name='Sheet1'):
    df = pd.read_excel(file_name, sheet_name=sheet_name, dtype=object)
    for ele in df.values:
        yield ele
