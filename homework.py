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
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

HOMEWORK_API = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = {
    'reviewing': 'Работа взята в ревью.',
    'rejected': 'К сожалению, в работе нашлись ошибки.',
    'approved': 'Ревьюеру всё понравилось, работа зачтена!'
}

bot = telegram.Bot(TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_name is None and homework_status is None:
        raise ValueError('Аргумент homework не правильной структуры.')

    verdict = HOMEWORK_STATUSES[homework_status]

    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    try:
        homework_statuses = requests.get(
            HOMEWORK_API,
            params={'from_date': current_timestamp},
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
        )
        return homework_statuses.json()
    except Exception:
        logger.exception()
        raise


def send_message(message):
    return bot.send_message(TELEGRAM_CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            homeworks_list = homeworks.get('homeworks')
            current_timestamp = homeworks.get('current_date')

            for homework in homeworks_list:
                message = parse_homework_status(homework)
                send_message(message)
                logger.info(f'Отправлено сообщение: {message}')
        except Exception as e:
            send_message(f'Бот упал с ошибкой: {e}')
            logger.exception()
        finally:
            time.sleep(5 * 60)


if __name__ == '__main__':
    logger.debug('Бот запустился')
    main()
