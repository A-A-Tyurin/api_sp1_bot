import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler('bot.log', maxBytes=50000000, backupCount=5)
handler.setFormatter(
    logging.Formatter('%(asctime)s, %(levelname)s, %(name)s, %(message)s')
)

logger.addHandler(handler)

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
HOMEWORK_API = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_status == 'reviewing':
        verdict = 'Работа взята в ревью.'
    if homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'

    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    homework_statuses = requests.get(
        HOMEWORK_API,
        params={'from_date': current_timestamp},
        headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    )
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    sleep_time = 5 * 60

    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            homeworks_list = homeworks.get('homeworks')

            for homework in homeworks_list:
                message = parse_homework_status(homework)
                send_message(message)
                logger.info(f'Отправлено сообщение: {message}')
        except Exception as e:
            send_message(f'Бот упал с ошибкой: {e}')
            logger.exception()
        finally:
            time.sleep(sleep_time)
            current_timestamp += sleep_time


if __name__ == '__main__':
    main()
