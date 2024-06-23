import pandas as pd


class DataManager:
    def __init__(self):
        self.shared_data = None

    def set_data(self, data: pd.DataFrame):
        if isinstance(data, pd.DataFrame):
            self.shared_data = data
        else:
            raise ValueError("Data must be a Pandas DataFrame")

    def get_data(self) -> pd.DataFrame:
        return self.shared_data

    def get_status(self) -> bool:
        if self.shared_data is None:
            return False
        return True


manager = DataManager()
