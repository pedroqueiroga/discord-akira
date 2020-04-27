from config import settings
from src.akira import Akira


ak = Akira()

ak.add_commands()

ak.run(settings.DISCORD_TOKEN)

print('fim?')
