import logging
import json
from config import MODEL_TEMPERATURE, IAM_TOKEN_PATH
import requests
from config import LOGS_PATH, MAX_MODEL_TOKENS, GPT_MODEL
from creds import get_creds

IAM_TOKEN, FOLDER_ID = get_creds()

logging.basicConfig(
    filename=LOGS_PATH,
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    filemode="w",
)


def count_tokens_in_dialogue(messages: list) -> int:
    iam_token = IAM_TOKEN
    folder_id = FOLDER_ID
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
        "maxTokens": MAX_MODEL_TOKENS,
        "messages": []
    }

    for row in messages:
        data["messages"].append(
            {
                "role": row["role"],
                "text": row["content"]
            }
        )

    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion",
            json=data,
            headers=headers
        ).json()["tokens"]
    )


def increment_tokens_by_request(messages: list[dict]):
    try:
        with open(IAM_TOKEN_PATH, "r") as token_file:
            tokens_count = json.load(token_file)["tokens_count"]

    except FileNotFoundError:
        tokens_count = 0

    current_tokens_used = count_tokens_in_dialogue(messages)
    tokens_count += current_tokens_used

    with open(IAM_TOKEN_PATH, "w") as token_file:
        json.dump({"tokens_count": tokens_count}, token_file)


def ask_gpt(messages):
    iam_token = IAM_TOKEN

    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
        "completionOptions": {
            "stream": False,
            "temperature": MODEL_TEMPERATURE,
            "maxTokens": MAX_MODEL_TOKENS
        },
        "messages": []
    }

    for row in messages:
        data["messages"].append(
            {
                "role": row["role"],
                "text": row["content"]
            }
        )

    try:
        response = requests.post(url, headers=headers, json=data)

    except Exception as e:
        print("Произошла непредвиденная ошибка.", e)

    else:
        if response.status_code != 200:
            print("Ошибка при получении ответа:", response.status_code)
        else:
            result = response.json()['result']['alternatives'][0]['message']['text']
            messages.append({"role": "assistant", "content": result})
            increment_tokens_by_request(messages)
            return result
