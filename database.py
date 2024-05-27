import sqlite3
import logging
from config import DB_NAME, DB_TABLE_USERS_NAME, LOGS_PATH

logging.basicConfig(
    filename=LOGS_PATH,
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    filemode="w",
)


def create_db():
    connection = sqlite3.connect(DB_NAME)
    connection.close()


def execute_query(query: str, data: tuple | None = None, db_name: str = DB_NAME):
    try:
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        if data:
            cursor.execute(query, data)
            connection.commit()

        else:
            cursor.execute(query)

    except sqlite3.Error as e:
        print("Ошибка при выполнении запроса: ", e)

    else:
        result = cursor.fetchall()
        connection.close()
        return result


def create_table():
    sql_query = (
        f"CREATE TABLE IF NOT EXISTS {DB_TABLE_USERS_NAME} "
        f"(id INTEGER PRIMARY KEY, "
        f"user_id INTEGER, "
        f"message TEXT"
        f"role TEXT,"
        f"total_gpt_tokens INTEGER,"
        f"tts_symbols INTEGER,"
        f"stt_blocks INTEGER;"
    )

    execute_query(sql_query)
    print("Таблица успешно создана")


def add_new_user(user_id: int):
    if not is_user_in_db(user_id):
        sql_query = (
            f"INSERT INTO {DB_TABLE_USERS_NAME} "
            f"(user_id, sessions) "
            f"VALUES (?, 0);"
        )

        execute_query(sql_query, (user_id,))
        print("Пользователь успешно добавлен")
    else:
        print("Пользователь уже существует!")


def add_message(user_id, full_message):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            message, role, total_gpt_tokens, tts_symbols, stt_blocks = full_message

            cursor.execute('''
                    INSERT INTO messages (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                           (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks)
                           )
            conn.commit()
            logging.info(f"DATABASE: INSERT INTO messages "
                         f"VALUES ({user_id}, {message}, {role}, {total_gpt_tokens}, {tts_symbols}, {stt_blocks})")
    except Exception as e:
        logging.error(e)
        return None


def count_users(user_id):
    try:

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()

            cursor.execute('''SELECT COUNT(DISTINCT user_id) FROM messages WHERE user_id <> ?''', (user_id,))
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        logging.error(e)
        return None


def select_n_last_messages(user_id, n_last_messages=4):
    messages = []
    total_spent_tokens = 0
    try:

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT message, role, total_gpt_tokens FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?''',
                           (user_id, n_last_messages))
            data = cursor.fetchall()
            if data and data[0]:

                for message in reversed(data):
                    messages.append({'text': message[0], 'role': message[1]})
                    total_spent_tokens = max(total_spent_tokens, message[2])

            return messages, total_spent_tokens
    except Exception as e:
        logging.error(e)
        return messages, total_spent_tokens


def count_all_limits(user_id, limit_type):
    try:

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''SELECT SUM({limit_type}) FROM messages WHERE user_id=?''', (user_id,))
            data = cursor.fetchone()

            if data and data[0]:
                logging.info(f"DATABASE: У user_id={user_id} использовано {data[0]} {limit_type}")
                return data[0]

            else:
                return 0

    except Exception as e:

        logging.error(e)
        return 0


def is_user_in_db(user_id: int) -> bool:
    sql_query = f"SELECT user_id " f"FROM {DB_TABLE_USERS_NAME} " f"WHERE user_id = ?;"
    return bool(execute_query(sql_query, (user_id,)))


def update_row(user_id: int, column_name: str, new_value: str | int | None):
    if is_user_in_db(user_id):
        sql_query = (
            f"UPDATE {DB_TABLE_USERS_NAME} "
            f"SET {column_name} = ? "
            f"WHERE user_id = ?;"
        )

        execute_query(sql_query, (new_value, user_id))
        print("Значение обновлено")

    else:
        print("Пользователь не найден в базе")


def get_user_data(user_id: int):
    if is_user_in_db(user_id):
        sql_query = (
            f"SELECT * "
            f"FROM {DB_TABLE_USERS_NAME} "
            f"WHERE user_id = {user_id}"
        )

        row = execute_query(sql_query)[0]
        result = {
            "messages": row[2],
            "role": row[3],
            "total_gpt_tokens": row[4],
            "tts_symbols": row[5],
            "stt_blocks": row[6],
        }
        return result


def count_all_blocks(user_id, db_name=DB_NAME):
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT SUM(stt_blocks) FROM messages WHERE user_id=?''', (user_id,))
            data = cursor.fetchone()

            if data and data[0]:
                return data[0]
            else:
                return 0
    except Exception as e:
        print(f"Error: {e}")

