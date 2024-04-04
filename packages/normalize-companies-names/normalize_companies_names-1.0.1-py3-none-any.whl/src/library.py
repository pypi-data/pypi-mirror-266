import pandas
from pandas import DataFrame
import os
from thefuzz import process
import thefuzz.fuzz as fuzz

def normalize_dataframe(df: DataFrame) -> DataFrame:
    print("Adjusting the order of the excel data found at the file...")
    wrong_pattern_column: str = df.columns.values[0]
    new_columns: list[str] = wrong_pattern_column.split(",")

    new_columns.insert(2, "to_delete")
    
    df[new_columns] = df[wrong_pattern_column].str.split(",", expand=True)
    
    df = df.drop([wrong_pattern_column, "to_delete"], axis=1)
    
    df.iloc[:, 1] = df.iloc[:, 1].str.replace(pat='"', repl="")
    df.iloc[:, 1] = df.iloc[:, 1].str.replace(pat='.', repl="")
    df.iloc[:, 1] = df.iloc[:, 1].str.replace(pat=' INC', repl="")
    df.iloc[:, 1] = df.iloc[:, 1].str.replace(pat=' INC.', repl="")
    df.iloc[:, 1] = df.iloc[:, 1].str.replace(pat=' LLP', repl="")
    df.iloc[:, 1] = df.iloc[:, 1].str.replace(pat=' LLC', repl="")
    df.iloc[:, 1] = df.iloc[:, 1].str.replace(pat='. LLC', repl="")

    print(f"Data found organized with the following columns: {df.columns}")
    return df

def load_data(path) -> DataFrame:
    file_path = os.path.realpath(path)

    if(not file_path.endswith(".xlsx") and not file_path.endswith(".xls")):
        raise TypeError("The file must be an excel type (e.g .xls or .xlsx)")
    
    df = pandas.read_excel(file_path)
    
    if(len(df.columns) == 1):
        df = normalize_dataframe(df)
        
    return df

def apply_normalized_name(df: DataFrame, canonicals: list[str]) -> DataFrame:
    return df["organization"].apply(
        lambda name: process.extractOne(name, canonicals, scorer=fuzz.ratio, score_cutoff=0.99)[0]
    )
    
def process_data(canonicals: list[str], read_file_path: str, destination_path: str):
    df = load_data(read_file_path)
        
    df["canonical_name"] = apply_normalized_name(df, canonicals)
    
    print("Normalized names went added to the excel, check the first element below: ", df.head(1), sep="\n")

    df.to_excel(f"{destination_path}output.xlsx")
    