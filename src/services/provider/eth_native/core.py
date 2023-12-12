from services.managers.mainnet.core import MainnetManager
from services.provider.base import BaseProvider
from web3 import Web3
from eth_account.account import LocalAccount

from utils.enums import CryptoCurrencies


class EthMainnetProvider(BaseProvider):
    """
    This module provides the core functionality for interacting with the Ethereum blockchain.
    """

    def __init__(self):
        self.web3 = MainnetManager().eth_web3
        super().__init__()

    def transfer(
        self,
        from_acct: LocalAccount,
        to_acct: LocalAccount,
        amount: float,
        crypto: CryptoCurrencies,
    ):
        """
        Transfers a specified amount of cryptocurrency from one account to another.

        Args:
          from_acct (LocalAccount): The account from which the cryptocurrency will be transferred.
          to_acct (LocalAccount): The account to which the cryptocurrency will be transferred.
          amount (float): The amount of cryptocurrency to transfer.
          crypto (CryptoCurrencies): The type of cryptocurrency to transfer.

        Returns:
          str: The transaction hash of the transfer.
        """
        if crypto != CryptoCurrencies.ETH:
            raise NotImplementedError("Only ETH is supported yet ")

        # Convert amount to wei
        wei = self.web3.to_wei(amount, "ether")

        # Build the transaction
        tx = {
            "chainId": 5,
            "to": Web3.to_checksum_address(to_acct.address),
            "value": wei,
            "gas": 1_500_000,
            "gasPrice": self.web3.eth.gas_price,
            "nonce": self.web3.eth.get_transaction_count(from_acct.address),
        }

        # Sign the transaction
        signed_tx = from_acct.sign_transaction(tx)

        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=900, poll_latency=10
        )

        return receipt
