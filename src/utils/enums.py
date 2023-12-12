from enum import Enum


class Operations(Enum):
    BRIDGE = "bridge"
    SWAP = "swap"


class Mainnet(Enum):
    ZKSYNC_ERA = "ZKSYNC_MAINNET"
    ETHEREUM = "ETHEREUM_MAINNET"


class CryptoCurrencies(Enum):
    ETH = "ETH"
    USDT = "USDT"


class SupportedTokenFarming(Enum):
    ZK_SYNC = "ZK_SYNC"
    IZUMI = "IZI"
