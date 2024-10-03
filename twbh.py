import os

import requests

from dotenv import load_dotenv



load_dotenv()
TG_API_PRO = os.getenv("BOT_TOKEN_PRO")
TG_API = os.getenv("BOT_TOKEN")

whook = 'marked-addia-ago-0dd6d371.koyeb.app'

r = requests.get(f"https://api.telegram.org/bot{TG_API}/setWebhook?url=https://{whook}/api/bot_actions/webhook/to_users")
print(r.json())
r_pro = requests.get(f"https://api.telegram.org/bot{TG_API_PRO}/setWebhook?url=https://{whook}/api/bot_actions/webhook/to_providers")
print(r_pro.json())