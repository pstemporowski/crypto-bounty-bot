import json
from math import floor
import os
import random
from subprocess import Popen, DEVNULL

import time
import pandas as pd
from services.managers.provider.core import ProviderManager
from utils.constants import (
    OPS_PATH,
    PIPE_PATH,
)
from utils.logger import logger
from utils.utils import singleton


@singleton
class BackgroundWorker:
    def __init__(self):
        self.operations = self.load_ops()
        self.pipes = self.read_pip()
        self.prov_mngr = ProviderManager()

    def run(self):
        logger.info(f"Worker on process: {os.getpid()}")
        while True:
            self.update_state()
            pipes_to_run = self.get_pipes_to_run()
            pipe_names = ", ".join(pipes_to_run["name"].astype(str))
            logger.info(f"running pipes: { pipe_names }")
            for index, row in pipes_to_run.iterrows():
                self.prov_mngr.exec_op_by_id(row["op_id"])
                self.update_next_exec_time(index)

            time.sleep(1000)

    def get_pipes_to_run(self):
        return self.pipes[
            (self.pipes["next_exec"] < time.time()) & (self.pipes["state"] == "active")
        ]

    def update_state(self):
        self.pipes = self.read_pip()
        self.ops = self.load_ops()

    def read_pip(self):
        return pd.read_csv(PIPE_PATH, index_col=0, header=0)

    def save_pipe(self):
        self.pipes.to_csv(PIPE_PATH)

    def load_ops(self):
        with open(OPS_PATH) as f:
            operations = json.load(f)
        if operations is None:
            print("No operations found, Exiting...")
            exit()

        return {x["id"]: x for x in operations}

    def load_pip(self):
        return pd.read_csv(PIPE_PATH, index_col=0, header=0)

    def update_next_exec_time(self, index):
        pipe = self.pipes.loc[index]
        repeat_every_time = pipe["repeat_every_time"]
        diff_time = pipe["diff_time"]

        next_exec_time = self.get_next_exec_time(repeat_every_time, diff_time)
        self.pipes.loc[index, "next_exec"] = floor(next_exec_time)
        self.save_pipe()

    def get_next_exec_time(self, repeat_every_time, diff_time):
        random_time = random.randint(-diff_time, diff_time)
        return time.time() + repeat_every_time + random_time

    def auto_dispose(self):
        active_pipes = self.pipes[self.pipes["state"] == "active"]
        if len(active_pipes) == 0:
            print("No active pipes, Exiting...")
            exit()
