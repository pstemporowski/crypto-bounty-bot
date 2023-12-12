from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def singleton(cls):
    inst = {}

    def getinstance():
        if cls not in inst:
            inst[cls] = cls()
        return inst[cls]

    return getinstance
