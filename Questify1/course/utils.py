import re
import os
import requests
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

API_URL = os.getenv("GPT_CHAT_API_URL")
API_KEY = os.getenv("GPT_CHAT_API_KEY")

def generate_quiz_questions(text: str) -> str:
    """
    Отправляет текст урока в GPT-чат и возвращает сырой ответ (строкой).
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "turbo",  # или другой доступный в gpt-chat.by
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты генератор тестов. Составь 5 тестовых вопросов по тексту "
                    "на русском языке. Каждый вопрос должен иметь варианты A-D "
                    "и указывать правильный ответ."
                )
            },
            {"role": "user", "content": text},
        ],
        "temperature": 0.7,
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    else:
        return f"Ошибка: {response.status_code}, {response.text}"


def parse_quiz_text(raw_text: str):
    """
    Преобразует сырой текст от модели в список словарей:
    [
        {
            "question": "Вопрос?",
            "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
            "answer": "A"
        }
    ]
    """
    if not raw_text:
        return []

    questions = []
    blocks = re.split(r"\n\d+\.\s", raw_text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Вопрос = первая строка
        q_match = re.match(r"(.*?)(?:\n|$)", block)
        question_text = q_match.group(1).strip() if q_match else ""

        # Варианты ответов
        options = re.findall(r"([A-DА-Гa-dа-г]\)\s.*)", block)

        # Правильный ответ
        answer_match = re.search(r"Правильный ответ[:\s]*([A-DА-Гa-dа-г])", block)
        answer = answer_match.group(1).strip() if answer_match else None

        questions.append({
            "question": question_text,
            "options": options,
            "answer": answer,
        })

    return questions