from config import settings
from src.akira import Akira
import os

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

ak = Akira()

ak.add_commands()

ak.run(DISCORD_TOKEN)

print('fim?')
