import pandas as pd


class DataManager:
    """
    A class to manage a shared Pandas DataFrame.

    The DataManager class provides methods to store, retrieve, and check the status of a
    Pandas DataFrame. This can be useful in scenarios where data needs to be shared
    or managed across different parts of an application.

    Attributes:
    ----------
    shared_data : pd.DataFrame or None
        A DataFrame to store the data provided by the user. Initialized to None.

    Methods:
    -------
    set_data(data: pd.DataFrame)
        Stores the provided DataFrame in the shared_data attribute.

    get_data() -> pd.DataFrame
        Returns the stored DataFrame.

    get_status() -> bool
        Returns True if a DataFrame is stored, otherwise False.

    Note:
    -------
    In later iterations and for production, the data manager should be replaced with a dash Data Store
    """

    def __init__(self):
        """
        Initializes the DataManager with no data.
        """
        self.shared_data = None

    def set_data(self, data: pd.DataFrame):
        """
        Stores the provided DataFrame.

        Parameters:
        ----------
        data : pd.DataFrame
            The DataFrame to store in the shared_data attribute.

        Raises:
        ------
        ValueError
            If the provided data is not a Pandas DataFrame.
        """
        if isinstance(data, pd.DataFrame):
            self.shared_data = data
        else:
            raise ValueError("Data must be a Pandas DataFrame")

    def get_data(self) -> pd.DataFrame:
        """
        Returns the stored DataFrame.

        Returns:
        -------
        pd.DataFrame
            The DataFrame stored in the shared_data attribute.
        """
        return self.shared_data

    def get_status(self) -> bool:
        """
        Checks if a DataFrame is stored.

        Returns:
        -------
        bool
            True if shared_data is not None, otherwise False.
        """
        return self.shared_data is not None


manager = DataManager()
