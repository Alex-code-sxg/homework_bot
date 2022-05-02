import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger(__name__)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        message_info = 'Сообщение отправлено в Telegram'
        logger.info(message_info)
    except Exception as error:
        error_send_message = f'Сообщение в Telegram не отправлено {error}'
        logger.error(error_send_message)
        raise Exception(error_send_message)


def get_api_answer(current_timestamp):
    """Делаем запрос к API, преобразуем ответ из JSON в формат Python."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != requests.codes.ok:
            error_api_answer = ('Произошла ошибка во время запроса.'
                                'Ответ API не получен')
            logger.error(error_api_answer)
            raise Exception(error_api_answer)
        return response.json()
    except requests.RequestException as error:
        message = f'Произошла ошибка во время запроса: {error}'
        logger.error(message)
        raise requests.RequestException(message)


def check_response(response):
    """Проверка ответа API на корректность."""
    if not isinstance(response, dict):
        error_response_api_dict = 'Формат response отличается от dict'
        logger.error(error_response_api_dict)
        raise TypeError(error_response_api_dict)
    homeworks = response.get('homeworks')
    if homeworks is None:
        error_response_api_key_homeworks = ('Ответ API не содержит ключ'
                                            ' homeworks')
        logger.error(error_response_api_key_homeworks)
        raise KeyError(error_response_api_key_homeworks)
    if not isinstance(homeworks, list):
        error_response_api_list = ('Формат данных homeworks'
                                   'отличается от list')
        logger.error(error_response_api_list)
        raise TypeError(error_response_api_list)
    return homeworks


def parse_status(homework):
    """Проверка изменения status домашней работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_name is None:
        error_parser_homework_name = ('Отсутсвует homework_name'
                                      ' домашней работы')
        logger.error(error_parser_homework_name)
        raise KeyError(error_parser_homework_name)
    if homework_status is None:
        error_parser_parser_status = 'Отсутсвует status домашней работы'
        logger.error(error_parser_parser_status)
        raise KeyError(error_parser_parser_status)
    if homework_status in HOMEWORK_STATUSES.keys():
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        error_parser_key_error = 'Отсутсвует status домашней работы'
        logger.error(error_parser_key_error)
        raise KeyError(error_parser_key_error)


def check_tokens():
    """Проверка наличия токенов."""
    if PRACTICUM_TOKEN is not None:
        if TELEGRAM_TOKEN is not None:
            if TELEGRAM_CHAT_ID is not None:
                return True
            logger.critical('Токен чата Telegram отсутствует')
            return False
        logger.critical('Токен Telegram отсутствует')
        return False
    logger.critical('Токен Практикума отсутствует')
    return False


def main():
    """Основная логика работы бота."""
    check = check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if check is False:
        return Exception('Что то пошло не так')
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
