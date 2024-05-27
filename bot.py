import telebot
from speechkit import speech_to_text
import database
import math
from validators import *
from yandex_gpt import ask_gpt, count_tokens_in_dialogue
from creds import get_bot_token
from config import (
    MAX_TTS_SYMBOLS, MAX_USER_TTS_SYMBOLS, MAX_USER_STT_BLOCKS, ADMINS,
    MAX_USERS, LOGS_PATH, COUNT_LAST_MSG
)


logging.basicConfig(
    filename=LOGS_PATH,
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    filemode="w",
)

bot = telebot.TeleBot(get_bot_token())

database.create_db()
database.create_table()


@bot.message_handler(commands=["start"])
def start(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    if not database.is_user_in_db(user_id):
        if len(database.get_user_data(user_id)) < MAX_USERS:
            database.add_new_user(user_id)
        else:

            bot.send_message(
                user_id,
                "К сожалению, лимит пользователей исчерпан. "
                "Вы не сможете воспользоваться ботом:("
            )
            return

    bot.send_message(
        user_id,
        f"Привет, {user_name}! Я бот-помощник, отправь мне голосовое или текст! "),


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id,
                     "Чтобы приступить к общению, отправь мне голосовое сообщение или текст")


@bot.message_handler(commands=["debug"])
def send_logs(message):
    user_id = message.from_user.id
    if user_id in ADMINS:
        with open(LOGS_PATH, "rb") as f:
            bot.send_document(message.from_user.id, f)


def is_tts_symbol_limit(message, text):
    user_id = message.from_user.id
    text_symbols = len(text)

    all_symbols = count_tokens_in_dialogue(user_id)
    if all_symbols is not None:
        all_symbols += text_symbols
    else:
        all_symbols = text_symbols

    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        bot.send_message(user_id, msg)
        return None

    if text_symbols >= MAX_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        bot.send_message(user_id, msg)
        return None

    return len(text)


@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    try:
        user_id = message.from_user.id

        status_check_users = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, "Произошла ошибка")
            return

        stt_blocks = is_stt_block_limit(user_id, message.voice.duration)
        if not stt_blocks:
            bot.send_message(user_id, 'Слишком длинное аудио')
            return

        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        status_stt, stt_text = speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return

        database.add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])
        last_messages, total_spent_tokens = database.select_n_last_messages(user_id, COUNT_LAST_MSG)
        total_gpt_tokens = is_gpt_token_limit(last_messages, total_spent_tokens)
        if not total_gpt_tokens:
            bot.send_message(user_id, "Исчерпан лимит токенов")
            return

        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return

        total_gpt_tokens += tokens_in_answer
        tts_symbols = is_tts_symbol_limit(user_id, answer_gpt)
        database.add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])

        if not tts_symbols:
            bot.send_message(user_id, "Испчерпан лимит")
            return

        status_tts, voice_response = speech_to_text(answer_gpt)
        if status_tts:
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
        else:
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

    except Exception as e:

        logging.error(e)
        bot.send_message(user_id, "Не получилось ответить. Попробуй записать другое сообщение")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:

        user_id = message.from_user.id

        status_check_users = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, "Превышено максимальное количество пользователей")
            return

        full_user_message = [message.text, 'user', 0, 0, 0]
        database.add_message(user_id=user_id, full_message=full_user_message)

        last_messages, total_spent_tokens = database.select_n_last_messages(user_id, COUNT_LAST_MSG)
        total_gpt_tokens = is_gpt_token_limit(last_messages, total_spent_tokens)
        if not total_gpt_tokens:
            bot.send_message(user_id, "Превышен общий лимит GPT-токенов")
            return

        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return

        total_gpt_tokens += tokens_in_answer
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        database.add_message(user_id=user_id, full_message=full_gpt_message)

        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

    except Exception as e:

        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")


@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id,
                     "Отправь мне голосовое или текстовое сообщение, и я тебе отвечу")


def is_stt_block_limit(message, duration):
    user_id = message.from_user.id

    audio_blocks = math.ceil(duration / 15)
    all_blocks = database.count_all_blocks(user_id)
    if all_blocks is not None:
        all_blocks += audio_blocks
    else:
        all_blocks = audio_blocks

    if duration >= 30:
        msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        bot.send_message(user_id, msg)
        return None

    if all_blocks >= MAX_USER_STT_BLOCKS:
        msg = f"Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}. Использовано {all_blocks} блоков. Доступно: {MAX_USER_STT_BLOCKS - all_blocks}"
        bot.send_message(user_id, msg)
        return None

    return audio_blocks


bot.infinity_polling()
