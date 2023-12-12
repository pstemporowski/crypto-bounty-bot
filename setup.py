from setuptools import find_packages, setup

setup(
    name="CryptoBountyBot",
    packages=find_packages(),
    entry_points={"console_scripts": ["cryptobountybot = crypto_bounty_bot.main:main"]},
    version=0.1,
)
