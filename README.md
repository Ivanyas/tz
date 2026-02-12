# Тестовое задание

## Что внутри

- `email_verifier.py` — проверка email-доменов (MX + SMTP)
- `telegram_sender.py` — отправка текста в Telegram
- `architecture.md` — архитектура email outreach на 1200 ящиков
- `ai-stack-blitz.md` — мой AI-стек

## Установка

```bash
# создаём виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# ставим зависимости
pip install dnspython requests
```

## 1. Проверка email

```bash
# один email
python email_verifier.py --email user@gmail.com

# список из файла
python email_verifier.py emails.txt
```

Проверяет:
- формат email
- наличие MX-записей
- SMTP handshake (существует ли пользователь)

## 2. Отправка в Telegram

Сначала нужен бот:
1. Создайте бота через @BotFather
2. Получите токен
3. Добавьте бота в чат
4. Узнайте chat_id через `https://api.telegram.org/bot<TOKEN>/getUpdates`

Запуск:
```bash
# через аргументы
python telegram_sender.py message.txt --token "BOT_TOKEN" --chat-id "CHAT_ID"

# или через .env файл
cp .env.example .env
# отредактируйте .env
python telegram_sender.py message.txt
```

## 3. Архитектура

См. [architecture.md](architecture.md)

## 4. AI-стек

См. [ai-stack-blitz.md](ai-stack-blitz.md)
