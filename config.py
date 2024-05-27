DB_NAME = 'database.db'

TABLE_NAME = 'texts'

DB_TABLE_USERS_NAME = "yandex_users"

ADMINS = [1606978710]

GPT_MODEL = "yandexgpt-lite"

MAX_MODEL_TOKENS = 64

MODEL_TEMPERATURE = 0.6

IAM_TOKEN_ENDPOINT = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"

MAX_GPT_TOKENS = 1200

COUNT_LAST_MSG = 4

MAX_USER_TTS_SYMBOLS = 5000

MAX_USER_GPT_TOKENS = 2000

MAX_USER_STT_BLOCKS = 7

MAX_USERS = 7

MAX_TTS_SYMBOLS = 1000

HOME_DIR = '/home/student/gpt_bot'

LOGS_PATH = f'{HOME_DIR}/logs.txt'

DB_FILE = f'{HOME_DIR}/messages.db'

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'

FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'

BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'

SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]

