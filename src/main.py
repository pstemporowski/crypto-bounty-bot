from dotenv import load_dotenv
from models.cryptobountybot_cli import CryptoBountyBotCLI


def main():
    load_dotenv()
    CryptoBountyBotCLI().start()


if __name__ == "__main__":
    main()
