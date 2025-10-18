# Questify — платформа для онлайн-курсов
Интерактивная платформа для обучения программированию с тестами и системой прогресса.
![Python](https://img.shields.io/badge/python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Описание

Questify — это обучающая платформа, где студенты могут проходить интерактивные курсы по Python, Django и машинному обучению.  
Каждый курс содержит уроки, тесты и визуальные материалы для лучшего усвоения материала.

## Установка и запуск

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/KozinetsJane/Questify.git
   cd questify
2. Создать виртуальное окружение и активировать его:
   ython -m venv venv
   source venv/bin/activate  # или venv\Scripts\activate на Windows
3. Установить зависимости:
   pip install -r requirements.txt
4. Провести миграции и запустить сервер:
   python manage.py migrate
   python manage.py runserver
5. Перейти в браузере на:
   http://127.0.0.1:8000

###  📂 Структура проекта
questify/
├── course/ # Приложение с курсами
├── users/ # Пользователи и аутентификация
├── static/ # CSS, JS, изображения
├── templates/ # HTML-шаблоны
├── manage.py
└── requirements.txt
## 6. 🧩 Используемые технологии
- Python 3.11
- Django 5.2.5
- SQLite
- Bootstrap 5
- HTML, CSS, JS
## Авторы

- **Kozinets Jane** — разработчик и дизайнер проекта  
  [GitHub](https://github.com/KozinetsJane) | [Telegram](https://t.me/Kozinets215)

