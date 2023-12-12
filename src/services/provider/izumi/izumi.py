from decimal import Decimal
import json
from math import floor
from services.managers.account.ers import ErsAccountManager
import time
from services.managers.mainnet.core import MainnetManager
from services.provider.base import BaseProvider
from web3 import Web3
from utils.logger import logger
from utils.constants import ERC_TOKEN_ABI_PATH, IZUMI_SWAP_ABI_PATH
from utils.enums import CryptoCurrencies
from eth_account.account import LocalAccount
from services.provider.izumi.addresses import Addresses
from web3.contract import Contract
from eth_abi.abi import encode


class IzumiProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self.mainnet_mngr = MainnetManager()
        self.swap_abi = self._read_abi(IZUMI_SWAP_ABI_PATH)
        self.erc_token_abi = self._read_abi(ERC_TOKEN_ABI_PATH)
        self.zk_web3 = self.mainnet_mngr.zk_web3

        self.swap_contract = self.get_contr(Addresses.SWAP_ADDR.value, self.swap_abi)

    def swap(
        self,
        acct: LocalAccount,
        amount: float,
        blockchain: "zksync",
        token_chain: list[str],
        fee_chain: list[int],
    ):
        """Swap on the ZKSync network

        Args:
            acct (LocalAccount): The account to swap with
            amount (float): The amount of ETH to swap
            token_chain (list[str]): The token chain to swap
            fee_chain (list[int]): The fee chain to swap
        """
        logger.info(
            f"Swapping with {amount} ETH to IZI over Izumi Finance. Address: {acct.address}"
        )
        # set the vals for the swap
        min_ecq = 0
        deadline = int(time.time()) + 10000
        decimal_amount = int(amount * (10**18))

        gas_price = self.zk_web3.eth.gas_price
        self.zk_web3.eth.default_account = acct.address
        checksum_addr = Web3.to_checksum_address(acct.address)
        nonce = self.zk_web3.eth.get_transaction_count(checksum_addr)
        path = self._get_token_chain_path(token_chain, fee_chain)
        tx_params = {
            "from": checksum_addr,
            "nonce": nonce,
            "gas": gas_price,
            "value": Web3.to_wei(amount, "ether"),
            "maxPriorityFeePerGas": Web3.to_wei(0.25, "gwei"),
            "maxFeePerGas": Web3.to_wei(0.25, "gwei"),
        }

        # init the function calls
        swap_cll = self.swap_contract.functions.swapAmount(
            (path, checksum_addr, decimal_amount, min_ecq, deadline)
        )

        refund_eth_cll = self.swap_contract.functions.refundETH()
        # encode the function calls to bytes[]
        encoded_clls = [self.encode_func_cll(x) for x in [swap_cll, refund_eth_cll]]
        # build the transaction
        multi_cll = self.swap_contract.functions.multicall(encoded_clls)
        signed_tx = self.build_and_sign_tx(multi_cll, tx_params, acct.key)
        # send the transaction
        tx = self.zk_web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        tx_receipt = self.zk_web3.eth.wait_for_transaction_receipt(
            tx,
            timeout=5000,
        )
        logger.info(f"Successfully swapped ETH to IZI")

    def build_and_sign_tx(self, cll, tx_params: dict, priv_key: str) -> dict:
        """Build and sign a transaction

        Args:
            tx_params (dict): The parameters for the transaction
            priv_key (str): The private key to sign with

        Returns:
            dict: The signed transaction
        """
        tx = self.build_tx(cll, tx_params)
        return self.sign_tx(tx, priv_key)

    def sign_tx(self, tx: dict, priv_key: str) -> dict:
        """Sign a transaction

        Args:
            tx (dict): The transaction to sign
            priv_key (str): The private key to sign with

        Returns:
            dict: The signed transaction
        """
        return self.zk_web3.eth.account.sign_transaction(tx, priv_key)

    def build_tx(self, cll, tx_params: dict) -> dict:
        """Build a transaction

        Args:
            tx_params (dict): The parameters for the transaction

        Returns:
            dict: The built transaction
        """
        if "gas" not in tx_params or tx_params["gas"] == 0:
            tx_params["gas"] = self.est_gas(cll, tx_params)
        tx_params["gas"] = 1_500_000
        return cll.build_transaction(tx_params)

    def est_gas(self, cll, tx_params: dict) -> int:
        """Estimate the gas for a transaction

        Args:
            tx_params (dict): The parameters for the transaction

        Returns:
            int: The estimated gas
        """
        tx = cll.build_transaction(tx_params)
        del tx["data"]
        return self.zk_web3.eth.estimate_gas(tx)

    def get_contr(self, addr: str, abi: list[dict]) -> Contract:
        """Get a contract from the address and abi

        Args:
            addr (str): The address of the contract
            abi (list[dict]): The abi of the contract

        Returns:
            Contract: The contract
        """

        return self.zk_web3.eth.contract(address=addr, abi=abi)

    def _get_token_chain_path(
        self, token_chain: list[str], fee_chain: list[int]
    ) -> str:
        """Get the token chain path for the swap

        Args:
            token_chain (list[str]): The token chain to swap
            fee_chain (list[int]): The fee chain to swap

        Returns:
            str: The token chain path
        """
        hex_out = token_chain[0]
        for i, fee in enumerate(fee_chain):
            hex_out += hex(fee)[2:].zfill(6)
            hex_out += token_chain[i + 1][2:]

        return hex_out

    def encode_func_cll(self, call):
        """Encode a function call to be used in a transaction

        Args:
            call (ContractFunction): The function to encode"""
        return self.swap_contract.encodeABI(fn_name=call.fn_name, args=call.args)

    def _get_token_contr(self, addr: str) -> dict:
        """Get the token contract for a given address

        Args:
            addr (str): The address of the token contract

        Returns:
            dict: The token contract
        """
        return self.zk_web3.eth.contract(address=addr, abi=self.erc_token_abi)
