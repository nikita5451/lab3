import logging
import requests
import telebot
from telebot import types

class HTTPLogHandler(logging.Handler):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def emit(self, record):
        if isinstance(record.msg, dict):
            data = record.msg.copy()
        else:
            data = {"message": record.getMessage()}
        data["level"] = record.levelname.lower()
        try:
            requests.post(self.url, json=data, timeout=1)
        except requests.RequestException:
            self.handleError(record)

logger = logging.getLogger("telegram_bot")
logger.setLevel(logging.INFO)
fluentd_url = "http://fluentd:8080/tg.telegram"
logger.addHandler(HTTPLogHandler(fluentd_url))

bot = telebot.TeleBot('-')

surname = ''
name = ''
group = ''
faculty = ''

@bot.message_handler(commands=['start'])
def start(message):
    logger.info({
        "event": "start_command",
        "user_id": message.from_user.id,
        "username": message.from_user.username
    })
    bot.send_message(message.from_user.id, 'Ваше прізвище?')
    bot.register_next_step_handler(message, get_surname)

@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def fallback(message):
    logger.info({
        "event": "fallback_text",
        "user_id": message.from_user.id,
        "text": message.text
    })
    bot.send_message(message.from_user.id, 'Напишіть /start, щоб почати')

def get_surname(message):
    global surname
    surname = message.text
    logger.info({
        "event": "got_surname",
        "user_id": message.from_user.id,
        "surname": surname
    })
    bot.send_message(message.from_user.id, 'Ваше імʼя?')
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    global name
    name = message.text
    logger.info({
        "event": "got_name",
        "user_id": message.from_user.id,
        "name": name
    })
    bot.send_message(message.from_user.id, 'Ваша група?')
    bot.register_next_step_handler(message, get_group)

def get_group(message):
    global group
    group = message.text
    logger.info({
        "event": "got_group",
        "user_id": message.from_user.id,
        "group": group
    })
    bot.send_message(message.from_user.id, 'Ваш факультет?')
    bot.register_next_step_handler(message, get_faculty)

def get_faculty(message):
    global faculty
    faculty = message.text
    logger.info({
        "event": "got_faculty",
        "user_id": message.from_user.id,
        "faculty": faculty
    })

    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Так', callback_data='yes')
    key_no = types.InlineKeyboardButton(text='Ні', callback_data='no')
    keyboard.add(key_yes, key_no)

    question = (
        f"Ваше прізвище та імʼя: {surname} {name}, "
        f"група {group}, факультет {faculty}. Все правильно?"
    )
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    logger.info({
        "event": "callback",
        "user_id": call.from_user.id,
        "choice": call.data
    })
    if call.data == "yes":
        bot.send_message(call.message.chat.id, 'Вас зареєстровано!')
        logger.info({
            "event": "registered",
            "user_id": call.from_user.id
        })
    else:
        bot.send_message(call.message.chat.id, 'Спробуйте ще раз!')

if __name__ == "__main__":
    logger.info({"event": "bot_start"})
    bot.polling(none_stop=True, interval=0)
