import pandas as pd
from abc import ABC, abstractmethod
from pandas.errors import EmptyDataError

COLS = ["priv_key", "addr", "balance", "last_updated"]


import pandas as pd
from abc import ABC, abstractmethod


class BaseAcountManager(ABC):
    """
    Base class for managing accounts.

    Args:
        accts_path (str): The path to the accounts file.

    Attributes:
        accts_path (str): The path to the accounts file.
        accts_df (pd.DataFrame): The DataFrame containing the account information.

    Methods:
        read_csv(accts_path: str) -> pd.DataFrame:
            Reads the accounts file and returns a DataFrame.
        save_accts_to_csv() -> None:
            Saves the account information to the accounts file.
        create_and_save_acct():
            Abstract method for creating and saving an account.
        get_balance(addr):
            Abstract method for getting the balance of an account.
    """

    def __init__(self, accts_path: str):
        self.accts_path = accts_path
        self.accts_df = self.read_csv(accts_path)

    def read_csv(self, accts_path: str) -> pd.DataFrame:
        """
        Reads the accounts file and returns a DataFrame.

        Args:
            accts_path (str): The path to the accounts file.

        Returns:
            pd.DataFrame: The DataFrame containing the account information.

        Raises:
            FileNotFoundError: If the accounts file is not found.
            EmptyDataError: If the accounts file is empty.
        """
        try:
            return pd.read_csv(accts_path)
        except FileNotFoundError:
            print("CSV file not found. Creating a new file when saving accounts.")
        except EmptyDataError:
            print("CSV file is empty")

        return pd.DataFrame(columns=COLS)

    def save_accts_to_csv(self) -> None:
        """
        Saves the account information to the accounts file.
        """
        self.accts_df.to_csv(self.accts_path, index=False)

    @abstractmethod
    def create_and_save_acct(self):
        """
        Abstract method for creating and saving an account.
        """
        raise NotImplementedError("should have implemented this")

    @abstractmethod
    def get_balance(self, addr):
        """
        Abstract method for getting the balance of an account.

        Args:
            addr: The address of the account.

        Returns:
            The balance of the account.
        """
        raise NotImplementedError("should have implemented this")
