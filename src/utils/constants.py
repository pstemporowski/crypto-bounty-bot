from utils.utils import get_project_root


PROJECT_ROOT = get_project_root()
PIPE_PATH = PROJECT_ROOT.joinpath("data/pipelines/pipelines.csv")
RUN_WORKER_SCRIPT_PATH = PROJECT_ROOT.joinpath("run-worker.py")
BACKGR_WORKER_LOG_PATH = PROJECT_ROOT.joinpath("data/logs/background_worker.log")
APP_LOG_PATH = PROJECT_ROOT.joinpath("data/logs/background_worker.log")
OPS_PATH = PROJECT_ROOT.joinpath("data/pipelines/operations.json")
TX_HISTORY_PATH = PROJECT_ROOT.joinpath("data/transactions.json")
ETH_SUGAR_DADDY_WALLETS_PATH = PROJECT_ROOT.joinpath(
    "data/wallets/sugar_daddy_wallets.csv"
)
FARMING_WALLETS_PATH = PROJECT_ROOT.joinpath("data/wallets/farming_wallets.csv")
IZUMI_SWAP_ABI_PATH = PROJECT_ROOT.joinpath("services/provider/izumi/swap/abi.json")
ERC_TOKEN_ABI_PATH = PROJECT_ROOT.joinpath("services/provider/erc_token/erc20.json")
