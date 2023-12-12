from abc import ABC, abstractmethod
import json


class BaseProvider(ABC):
    def __init__(self):
        super().__init__()

    def _read_abi(self, abi_path):
        with open(abi_path, "r") as f:
            return json.load(f)
