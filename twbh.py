import os

import requests

from dotenv import load_dotenv



load_dotenv()
TG_API = os.getenv("BOT_TOKEN_PRO")

whook = 'ago-ago-8570935a.koyeb.app'

r = requests.get(f"https://api.telegram.org/bot{TG_API}/setWebhook?url=https://{whook}/api/bot_actions/webhook/to_providers")
print(r.json())