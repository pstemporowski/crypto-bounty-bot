from models.background_worker import BackgroundWorker
import os
from dotenv import load_dotenv
from utils.logger import logger


def main():
    load_dotenv()
    BackgroundWorker().run()


if __name__ == "__main__":
    main()
