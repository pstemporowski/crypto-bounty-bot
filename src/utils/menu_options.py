import os
from subprocess import Popen, DEVNULL
import pandas as pd
from PyInquirer import Validator
import subprocess
from utils.logger import logger

from utils.constants import (
    BACKGR_WORKER_LOG_PATH,
    PIPE_PATH,
    RUN_WORKER_SCRIPT_PATH,
)


class MenuOption:
    instances = []

    def __init__(
        self,
        name: str = "",
        msg: str = "",
        choices: list = None,
        type: str = None,
        validator: Validator = None,
        style=None,
        funcs: list = None,
        async_funcs=None,
    ):
        self.name = name
        self.msg = msg
        self.choices = choices or ["Back"]
        self.type = type
        self.validator = validator
        self.style = style
        self.funcs = funcs or []
        self.async_funcs = async_funcs or []
        self.__class__.instances.append(self)

    def __str__(self):
        return self.name

    def call_funcs(self):
        for func in self.funcs:
            func(self)

    def to_question(self):
        return {
            "type": self.type,
            "name": self.name,
            "message": self.msg,
            "choices": self.choices,
            "validate": self.validator,
        }

    @classmethod
    def get_inst_dict(cls):
        return {menu_option.name: menu_option for menu_option in MenuOption.instances}


def start_worker(self):
    cmd = [
        "nohup",
        "python",
        RUN_WORKER_SCRIPT_PATH,
    ]
    with open(BACKGR_WORKER_LOG_PATH, "a") as log_file:
        Popen(
            cmd,
            stdout=log_file,
            stderr=log_file,
            stdin=DEVNULL,
            close_fds=True,
            start_new_session=True,
            preexec_fn=os.setpgrp,
        )


def stop_worker(self):
    cmd = ["pkill", "-f", str(RUN_WORKER_SCRIPT_PATH)]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    is_terminated = process.wait() == 0

    if is_terminated:
        logger.info("Worker terminated succesfully")
    return is_terminated


def get_worker_state():
    cmd = ["pgrep", "-f", "python " + str(RUN_WORKER_SCRIPT_PATH)]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        proc.wait()
        out, _ = proc.communicate()
        if out is None:
            return False
        else:
            return len(out.decode()) > 0


def set_choices_on_worker_state(self: MenuOption):
    if get_worker_state():
        self.msg = "Background Worker is running"
        self.choices = [STOP_BCKGR_WORKER_MENU.name, "Back"]
    else:
        self.msg = "Background Worker is not running"
        self.choices = [START_BCKGR_WORKER_MENU.name, "Back"]


def set_choices(self: MenuOption):
    pipes = pd.read_csv(PIPE_PATH, index_col=0, header=0)
    self.choices = [
        f"({state}) {name} " for name, state in zip(pipes.name, pipes.state)
    ]
    self.choices.append("Back")


SUGGAR_DADDY_WALLET_MANAGER = MenuOption(
    "Sugar Daddy Wallets",
    type="list",
    choices=["Import Wallets", "Delete Wallets", "Back"],
    validator=None,
    msg="Choose the operation you want to perform on Sugar Daddy Wallets",
)

FARMING_WALLET_MANAGER = MenuOption(
    "Farming Wallets",
    type="list",
    msg="Choose the operation you want to perform on Farming Wallets",
    choices=["Import Wallets", "Delete Wallets", "Back"],
    validator=None,
)

FARM_LAYERZERO_MENU = MenuOption(
    "Farm LayerZero",
    type="list",
    choices=[
        "ZK Sync",
        "LayerZero",
        "Back",
    ],
    msg="What do you want to farm?",
)

CHOOSE_WALLET_TYPE_MENU = MenuOption(
    "Manage Wallets",
    type="list",
    msg="What kind of wallet do you want to manage?",
    choices=[
        SUGGAR_DADDY_WALLET_MANAGER.name,
        FARMING_WALLET_MANAGER.name,
        "Back",
    ],
)

MANAGE_STRATEGIES_MENU = MenuOption(
    "Manage Farming Strategies",
    type="list",
    funcs=[set_choices],
    msg="What do you want to farm?",
)

STOP_BCKGR_WORKER_MENU = MenuOption(
    "Stop Worker",
    type="list",
    funcs=[stop_worker],
    choices=[
        "Back",
    ],
    msg="Succesful stopped the background worker",
)


START_BCKGR_WORKER_MENU = MenuOption(
    "Start Worker",
    type="list",
    funcs=[start_worker],
    choices=[
        "Back",
    ],
    msg="Succesful started the background worker",
)

MANAGE_BCKGRD_WORKER_MENU = MenuOption(
    "Manage Background Worker",
    type="list",
    choices=None,
    funcs=[set_choices_on_worker_state],
    msg="Choose if you want to start or stop the background worker",
)

SETTINGS_MENU = MenuOption(
    "Settings",
    type="list",
    choices=[
        "Sleep Time",
        "Back",
    ],
    msg="Choose the Operation you want to perform",
)

MAIN_MENU = MenuOption(
    "Main Menu",
    type="list",
    choices=[
        MANAGE_STRATEGIES_MENU.name,
        CHOOSE_WALLET_TYPE_MENU.name,
        MANAGE_BCKGRD_WORKER_MENU.name,
        SETTINGS_MENU.name,
        "Exit",
    ],
    msg="Choose the Operation you want to perform",
)


NOT_SUPPORTED = MenuOption(
    "Not Supported",
    type="list",
    choices=["Back"],
    msg="This Operation is not supported yet.",
)
