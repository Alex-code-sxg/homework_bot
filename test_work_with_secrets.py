import os

from dotenv import load_dotenv

load_dotenv()
# Теперь переменная TOKEN, описанная в файле .env,
# доступна в пространстве переменных окружения

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
print(PRACTICUM_TOKEN)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
print(TELEGRAM_TOKEN)

TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
print(TELEGRAM_CHAT_ID)
