import pandas as pd


class DataMinig():

    @staticmethod
    def csv_to_dataframe(file_path):
        df = pd.read_csv(file_path)
        return df