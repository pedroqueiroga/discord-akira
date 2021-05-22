import asyncio

from config import settings
from src.akira import Akira


def main():
    ak = Akira()
    ak.add_commands()

    ak.run(settings.DISCORD_TOKEN)

    print('cleaning up...')

    clean_up(ak)

    print('fim?')


def clean_up(ak):
    asyncio.run(ak.close())
    print('logged out')


main()
