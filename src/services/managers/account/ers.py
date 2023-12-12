import os
from eth_account import Account
from web3 import HTTPProvider, Web3
from services.managers.account.base import BaseAcountManager
from eth_account.account import LocalAccount
from utils.logger import logger


class ErsAccountManager(BaseAcountManager):
    """
    ErsAccountManager is a class that manages Ethereum accounts for the ERS system.

    Args:
        addr_path (str): The file path to the address file.

    Attributes:
        accts_df (pandas.DataFrame): A DataFrame that stores the Ethereum accounts.

    Methods:
        get_priv_key(addr): Returns the private key for a given Ethereum address.
        get_eth_accts(): Returns a list of all Ethereum accounts.
        create_and_save_acct(): Creates a new Ethereum account and saves it to the DataFrame.
        get_balance(addr): Returns the balance of a given Ethereum address.

    """

    def __init__(self, addr_path):
        super().__init__(addr_path)

    def get_priv_key(self, addr):
        """
        Returns the private key for a given Ethereum address.

        Args:
            addr (str): The Ethereum address.

        Returns:
            str: The private key associated with the address.

        """
        return self.accts_df.get(addr)

    def get_eth_accts(self) -> list[LocalAccount]:
        """
        Returns a list of all Ethereum accounts.

        Returns:
            list[LocalAccount]: A list of LocalAccount objects representing the Ethereum accounts.

        """
        return self.accts_df.apply(
            lambda row: Account.from_key(row["priv_key"]), axis=1
        ).tolist()

    def create_and_save_acct(self) -> LocalAccount:
        """
        Creates a new Ethereum account and saves it to the DataFrame.

        Returns:
            LocalAccount: The newly created Ethereum account.

        """
        acct = Account.create()
        logger.info(f"Created new account: {acct.address}")
        self.accts_df.loc[len(self.accts_df)] = [
            acct.key.hex(),
            acct.address,
            None,
            None,
        ]
        self.save_accts_to_csv()
        return acct

    @staticmethod
    def get_balance(addr):
        """
        Returns the balance of a given Ethereum address.

        Args:
            addr (str): The Ethereum address.

        Returns:
            float: The balance of the address in Ether.

        """
        eth_web = Web3(HTTPProvider(os.environ["ETH_URL"]))
        balance = eth_web.eth.get_balance(addr)
        return eth_web.from_wei(balance, "ether")
