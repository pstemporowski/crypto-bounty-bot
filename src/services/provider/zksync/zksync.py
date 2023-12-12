import time
from services.managers.account.ers import ErsAccountManager
from services.provider.base import BaseProvider
from utils.enums import Mainnet, Operations, CryptoCurrencies
from eth_account.signers.local import LocalAccount
from zksync2.core.types import Token
from zksync2.manage_contracts.zksync_contract import ZkSyncContract
from zksync2.provider.eth_provider import EthereumProvider
from zksync2.transaction.transaction_builders import TxFunctionCall
from zksync2.core.types import ZkBlockParams, EthBlockParams
from zksync2.signer.eth_signer import PrivateKeyEthSigner
from eth_utils import to_checksum_address
from eth_typing import HexStr
from web3 import Web3
from services.managers.mainnet.core import MainnetManager
from utils.utils import singleton
from utils.logger import logger


@singleton
class ZksyncEraProvider(BaseProvider):
    """
    ZksyncEraProvider is a provider for interacting with the ZkSync Era network.
    It supports bridging and transferring ETH between L2 and L1 networks.
    """

    SUPPORTED_OPS = {
        Operations.BRIDGE: {
            (Mainnet.ETHEREUM, Mainnet.ZKSYNC_ERA): [
                CryptoCurrencies.ETH,
            ],
            (Mainnet.ZKSYNC_ERA, Mainnet.ETHEREUM): [
                CryptoCurrencies.ETH,
            ],
        },
    }

    def __init__(self):
        """
        Initialize the ZksyncEraProvider.
        """
        mainnet_mngr = MainnetManager()
        self.zk_web3 = mainnet_mngr.zk_web3
        self.eth_web3 = mainnet_mngr.eth_web3
        super().__init__()

    def get_balance(self, token: CryptoCurrencies, acc: LocalAccount) -> float:
        """
        Get the balance of the account.

        Args:
            token (CryptoCurrencies): The token for which the balance will be returned.
            acc (LocalAccount): The local account used for signing transactions.

        Returns:
            float: The balance of the account.
        """
        zk_web = self.zk_web3

        if token == CryptoCurrencies.ETH:
            balance_wei = zk_web.zksync.get_balance(
                acc.address, EthBlockParams.LATEST.value
            )

            balance_eth = Web3.from_wei(balance_wei, "ether")

            return balance_eth
        else:
            raise NotImplementedError("Only ETH is supported")

    def bridge(
        self,
        acct: LocalAccount,
        from_net: Mainnet,
        to_net: Mainnet,
        token: CryptoCurrencies,
        amount: float,
    ) -> tuple[HexStr, HexStr]:
        """
        Bridge ETH from L2 to L1 network.

        Args:
            acct (LocalAccount): The local account used for signing transactions.
            from_net (Mainnet): From which network the withdrawal will be made.
            to_net (Mainnet): To which network the withdrawal will be made.
            token (CryptoCurrencies): Which token will be bridged.
            amount (float): How much the withdrawal will contain.

        Returns:
            tuple[HexStr, HexStr]: Deposit transaction hashes on L1 and L2 networks.
        """
        if (
            from_net == Mainnet.ETHEREUM
            and to_net == Mainnet.ZKSYNC_ERA
            and token == CryptoCurrencies.ETH
        ):
            return self._bridge_eth_to_zksync_era(amount, acct)

    def transfer(
        self,
        from_acct: LocalAccount,
        to_acct: LocalAccount,
        net: Mainnet,
        token: CryptoCurrencies,
        amount: float,
    ) -> HexStr:
        """
        Transfer ETH from L2 to L1 network.

        Args:
            net (Mainnet): The network to transfer from
            token (CryptoCurrencies): The token to transfer
            from_acct (LocalAccount): The account to transfer from
            to_acct (LocalAccount): The account to transfer to
            amount (float): The amount to transfer

        Raises:
            NotImplementedError: If the transfer is not supported

        Returns:
            HexStr: The transaction hash of the transfer
        """
        if net == Mainnet.ZKSYNC_ERA and token == CryptoCurrencies.ETH:
            return self._transfer_eth(from_acct, to_acct, amount)
        else:
            raise NotImplementedError(
                "Only transferring ETH on ZKSYNC_ERA is supported"
            )

    def transfer_and_bridge(
        self,
        from_acct: LocalAccount,
        to_acct: LocalAccount,
        from_net: Mainnet,
        to_net: Mainnet,
        token: CryptoCurrencies,
        amount: float,
    ):
        if (
            from_net == Mainnet.ETHEREUM
            and to_net == Mainnet.ZKSYNC_ERA
            and token == CryptoCurrencies.ETH
        ):
            return self._transfer_and_bridge_eth_to_zksync_era(
                from_acct, to_acct, amount
            )
        else:
            raise NotImplementedError(
                "Only transferring ETH on ZKSYNC_ERA is supported"
            )

    def _transfer_eth(
        self, from_acct: LocalAccount, to_acc: LocalAccount, amount: float
    ) -> HexStr:
        """
        Transfer ETH to a desired address on zkSync network.

        Args:
            from_acct (LocalAccount): The account to transfer from
            to_acc (LocalAccount): The account to transfer to
            amount (float): The amount of ETH to transfer

        Returns:
            HexStr: The transaction hash of the transfer
        """
        # Get chain id of zkSync network
        chain_id = self.zk_web3.zksync.chain_id

        # Signer is used to generate signature of provided transaction
        signer = PrivateKeyEthSigner(self.acc, chain_id)

        # Get nonce of ETH address on zkSync network
        nonce = self.zk_web3.zksync.get_transaction_count(
            self.account.address, ZkBlockParams.COMMITTED.value
        )

        # Get current gas price in Wei
        gas_price = self.zk_web3.zksync.gas_price

        # Create transaction
        tx_func_call = TxFunctionCall(
            chain_id=5,
            nonce=nonce,
            from_=from_acct.address,
            to=to_checksum_address(to_acc.address),
            value=self.zk_web3.to_wei(amount, "ether"),
            data=HexStr("0x"),
            gas_limit=0,  # UNKNOWN AT THIS STATE
            gas_price=gas_price,
            max_priority_fee_per_gas=100_000_000,
        )

        # ZkSync transaction gas estimation
        est_gas = self.zk_web3.zksync.eth_estimate_gas(tx_func_call.tx)

        # Convert transaction to EIP-712 format
        tx_712 = tx_func_call.tx712(est_gas)

        # Sign message & encode it
        signed_message = signer.sign_typed_data(tx_712.to_eip712_struct())

        # Encode signed message
        msg = tx_712.encode(signed_message)

        # Transfer ETH
        tx_hash = self.zk_web3.zksync.send_raw_transaction(msg)
        # Wait for transaction to be included in a block
        tx_receipt: self.zk_web3.zksync.wait_for_transaction_receipt(
            tx_hash, timeout=10000, poll_latency=10
        )

        # Return the transaction hash of the transfer
        return tx_hash.hex()

    def _transfer_and_bridge_eth_to_zksync_era(
        self,
        from_acct: LocalAccount,
        to_acct: LocalAccount,
        amount: float,
    ):
        logger.info(
            f"Transferring and bridging ETH from (Mainnet) {from_acct.address} to (Zksync Era) {to_acct.address}"
        )
        eth_prov = EthereumProvider(self.zk_web3, self.eth_web3, from_acct)
        l1_tx_receipt = eth_prov.deposit(
            to=to_acct.address,
            token=Token.create_eth(),
            amount=Web3.to_wei(amount, "ether"),
            gas_price=self.eth_web3.eth.gas_price,
        )

        # Check if deposit transaction was successful
        if not l1_tx_receipt["status"]:
            raise RuntimeError("Deposit transaction on L1 network failed")

        # Get ZkSync contract on L1 network
        zksync_contr = ZkSyncContract(
            self.zk_web3.zksync.main_contract_address, self.eth_web3, from_acct
        )

        # Get hash of deposit transaction on L2 network
        l2_hash = self.zk_web3.zksync.get_l2_hash_from_priority_op(
            l1_tx_receipt, zksync_contr
        )

        # Wait for deposit transaction on L2 network to be finalized (5-7 minutes)

        l2_tx_receipt = self.zk_web3.zksync.wait_for_transaction_receipt(
            transaction_hash=l2_hash, timeout=360, poll_latency=10
        )
        logger.info(f"Successfully transfered and bridged ETH")
        # return deposit transaction hashes from L1 and L2 networks
        return (
            l1_tx_receipt["transactionHash"].hex(),
            l2_tx_receipt["transactionHash"].hex(),
        )

    def _bridge_eth_to_zksync_era(
        self,
        amount: float,
        acct: LocalAccount,
    ) -> tuple[HexStr, HexStr]:
        """
        Bridge ETH from L2 to L1 network.

        Args:
            amount (float): How much the withdrawal will contain.
            acct (LocalAccount): The local account used for signing transactions.

        Returns:
            tuple[HexStr, HexStr]: Deposit transaction hashes on L1 and L2 networks.
        """

        eth_prov = EthereumProvider(self.zk_web3, self.eth_web3, acct)
        l1_tx_receipt = eth_prov.deposit(
            to=acct.address,
            token=Token.create_eth(),
            amount=Web3.to_wei(amount, "ether"),
            gas_price=self.eth_web3.eth.gas_price,
        )

        # Check if deposit transaction was successful
        if not l1_tx_receipt["status"]:
            raise RuntimeError("Deposit transaction on L1 network failed")

        # Get ZkSync contract on L1 network
        zksync_contr = ZkSyncContract(
            self.zk_web3.zksync.main_contract_address, self.eth_web3, acct
        )

        # Get hash of deposit transaction on L2 network
        l2_hash = self.zk_web3.zksync.get_l2_hash_from_priority_op(
            l1_tx_receipt, zksync_contr
        )

        # Wait for deposit transaction on L2 network to be finalized (5-7 minutes)
        print(
            "Waiting for deposit transaction on L2 network to be finalized (5-7 minutes)"
        )
        l2_tx_receipt = self.zk_web3.zksync.wait_for_transaction_receipt(
            transaction_hash=l2_hash, timeout=360, poll_latency=10
        )
        print("Deposit transaction on L2 network was finalized")
        # return deposit transaction hashes from L1 and L2 networks
        return (
            l1_tx_receipt["transactionHash"].hex(),
            l2_tx_receipt["transactionHash"].hex(),
        )
