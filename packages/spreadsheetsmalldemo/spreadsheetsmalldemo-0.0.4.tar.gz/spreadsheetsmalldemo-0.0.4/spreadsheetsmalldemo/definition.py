import pandas as pd
import os

class Spreadsheet:
    def __init__(self):
        pass

    def get_dataframe_filtered(self, file_path: str, sheet_name: str, column: str, value: str):
        dataframe = pd.read_excel(file_path, sheet_name=sheet_name)
        filtered_dataframe = dataframe[dataframe[column] == value]
        return filtered_dataframe
    
    def check_file_exists(self, file_path: str):
        if os.path.exists(file_path):
            return True
        return False