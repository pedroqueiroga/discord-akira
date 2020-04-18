from config import settings
from src.terraplanista import Terraplanista
import os

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

br = Terraplanista()

br.add_commands()

br.run(DISCORD_TOKEN)

print('fim?')
