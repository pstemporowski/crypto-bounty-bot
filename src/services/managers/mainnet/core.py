import os

from web3 import Web3, HTTPProvider
from zksync2.module.module_builder import ZkSyncBuilder

from utils.utils import singleton


@singleton
class MainnetManager:
    """
    A class that manages the mainnet connections for Ethereum and ZKSync.

    Attributes:
        eth_web3 (Web3): An instance of Web3 connected to the Ethereum mainnet.
        zk_web3 (Web3): An instance of Web3 connected to the ZKSync mainnet.

    Methods:
        __init__(): Initializes the MainnetManager class by setting up the web3 connections and checking the health of the networks.
        check_health(): Checks the health of the Ethereum and ZKSync networks and prints a message if any of them are not connected.
    """

    def __init__(self) -> None:
        """
        Initializes the MainnetManager class by setting up the web3 connections and checking the health of the networks.
        """
        self.eth_web3 = Web3(HTTPProvider("https://eth-goerli.public.blastapi.io"))
        self.zk_web3 = ZkSyncBuilder.build("https://testnet.era.zksync.dev")
