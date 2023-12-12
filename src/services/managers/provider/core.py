import json
from services.managers.account.ers import ErsAccountManager
from services.provider.eth_native.core import EthMainnetProvider
from services.provider.izumi.izumi import IzumiProvider
from services.provider.zksync.zksync import ZksyncEraProvider
from utils.constants import ETH_SUGAR_DADDY_WALLETS_PATH, FARMING_WALLETS_PATH, OPS_PATH
from utils.enums import CryptoCurrencies, Mainnet
from utils.logger import logger

import json


class ProviderManager:
    """
    The ProviderManager class manages various providers and operations related to cryptocurrency transactions.

    Attributes:
        izumi_prov (IzumiProvider): An instance of the IzumiProvider class.
        zk_sync_prov (ZksyncEraProvider): An instance of the ZksyncEraProvider class.
        farming_acct_mngr (ErsAccountManager): An instance of the ErsAccountManager class for farming wallets.
        sd_acct_mngr (ErsAccountManager): An instance of the ErsAccountManager class for Sugar Daddy wallets.
        ops (set): A set of operation IDs.

    Methods:
        read_operations(): Reads the operations from a file and returns a set of operation IDs.
        exec_op_by_id(op_id): Executes an operation based on the given operation ID.
        generate_wallet(details): Generates new wallets and transfers funds.
        bridge(details): Bridges funds between different blockchains.
        swap(details): Swaps tokens between different chains.
    """

    def __init__(self):
        self.izumi_prov = IzumiProvider()
        self.zk_sync_prov = ZksyncEraProvider()
        self.eth_net_prov = EthMainnetProvider()
        self.farming_acct_mngr = ErsAccountManager(FARMING_WALLETS_PATH)
        self.sugar_daddy_acct = ErsAccountManager(ETH_SUGAR_DADDY_WALLETS_PATH)
        self.ops = self.read_operations()

    def read_operations(self):
        """
        Reads the operations from a file and returns a set of operation IDs.

        Returns:
            set: A set of operation IDs.
        """
        with open(OPS_PATH, "r") as f:
            ops = json.load(f)
            return {x["id"]: x for x in ops}

    def exec_op_by_id(self, op_id):
        """
        Executes an operation based on the given operation ID.

        Args:
            op_id (int): The ID of the operation to be executed.
        """
        op = self.ops[op_id]
        logger.info(f"Executing operation: {op['name']}")
        if "generate_wallet" and "swap" in op["name"]:
            self.generate_wallet_and_swap(op["details"])
        elif "generate_wallet" in op["name"]:
            self.generate_wallet(op["details"])
        elif "swap" in op["name"]:
            self.swap(op["details"])
        else:
            logger.warning(f"Cant find operation: {op['name']}")

        logger.info(f"Finished executing operation: {op['name']}")

    def generate_wallet_and_swap(self, details: dict):
        """
        Generates new wallets and transfers funds.

        Args:
            details (dict): A dictionary containing the details of the wallet generation.
        """
        self.generate_wallet(details)
        self.swap(details)

    def generate_wallet(self, details: dict):
        new_addrs_count = details["wallet_count"]
        feed_amount = details["feed_amount"]
        sugar_daddy_acct = self.sugar_daddy_acct.get_eth_accts()[0]

        for _ in range(new_addrs_count):
            acct = self.farming_acct_mngr.create_and_save_acct()

            self.zk_sync_prov.transfer_and_bridge(
                sugar_daddy_acct,
                acct,
                Mainnet.ETHEREUM,
                Mainnet.ZKSYNC_ERA,
                CryptoCurrencies.ETH,
                feed_amount,
            )

        logger.info(f"Successfully generated {new_addrs_count} new wallets")

    def bridge(self, details: dict):
        """
        Bridges funds between different blockchains.

        Args:
            details (dict): A dictionary containing the details of the bridging operation.
        """
        from_blockchain = details["from"]
        to_blockchain = details["to"]

        if from_blockchain == "ETH" and to_blockchain == "ZKSYNC":
            for acct in self.farming_acct_mngr.get_eth_accts():
                self.zk_sync_prov.bridge(
                    acct,
                    Mainnet.ETHEREUM,
                    Mainnet.ZKSYNC_ERA,
                    CryptoCurrencies.ETH,
                    0.01,
                )

    def swap(self, details: dict):
        """
        Swaps tokens between different chains.

        Args:
            details (dict): A dictionary containing the details of the swapping operation.
        """
        swap_fraction = details["swap_fraction"]
        balance = 0.01
        for acct in self.farming_acct_mngr.get_eth_accts():
            self.izumi_prov.swap(
                acct,
                balance * swap_fraction,
                blockchain=Mainnet.ZKSYNC_ERA,
                token_chain=[
                    "0x8C3e3f2983DB650727F3e05B7a7773e4D641537B",
                    "0xA5900cce51c45Ab9730039943B3863C822342034",
                ],
                fee_chain=[2000],
            )
