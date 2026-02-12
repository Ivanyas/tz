#!/usr/bin/env python3
"""
Отправка текста из файла в Telegram

Запуск:
    python telegram_sender.py message.txt
    python telegram_sender.py message.txt --token BOT_TOKEN --chat-id CHAT_ID
"""

import sys
import os
import argparse
import requests
from pathlib import Path


class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id, text, parse_mode=None):
        # лимит телеграма — 4096 символов
        if len(text) > 4096:
            return self._send_long_message(chat_id, text, parse_mode)

        params = {"chat_id": chat_id, "text": text}
        if parse_mode:
            params["parse_mode"] = parse_mode

        resp = requests.post(f"{self.api_url}/sendMessage", json=params, timeout=30)
        data = resp.json()

        if data.get("ok"):
            return {"success": True, "message_id": data["result"]["message_id"]}
        else:
            return {"success": False, "error": data.get("description", "Unknown error")}

    def _send_long_message(self, chat_id, text, parse_mode=None):
        # разбиваем на части по строкам
        parts = []
        current = ""

        for line in text.split("\n"):
            if len(current) + len(line) + 1 > 4096:
                if current:
                    parts.append(current)
                current = line
            else:
                current = current + "\n" + line if current else line

        if current:
            parts.append(current)

        # отправляем каждую часть
        last_result = None
        for i, part in enumerate(parts, 1):
            prefix = f"[{i}/{len(parts)}]\n" if len(parts) > 1 else ""
            result = self.send_message(chat_id, prefix + part, parse_mode)
            last_result = result
            if not result["success"]:
                return result

        return last_result


def load_config(args):
    # приоритет: аргументы > .env > переменные окружения
    token = args.token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = args.chat_id or os.getenv("TELEGRAM_CHAT_ID")

    # пробуем .env файл
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                if key == "TELEGRAM_BOT_TOKEN" and not token:
                    token = value
                elif key == "TELEGRAM_CHAT_ID" and not chat_id:
                    chat_id = value

    if not token:
        print("Ошибка: не указан TELEGRAM_BOT_TOKEN")
        print("Укажите через --token или в .env файле")
        sys.exit(1)

    if not chat_id:
        print("Ошибка: не указан TELEGRAM_CHAT_ID")
        print("Укажите через --chat-id или в .env файле")
        sys.exit(1)

    return {"token": token, "chat_id": chat_id}


def main():
    parser = argparse.ArgumentParser(description="Отправка текста в Telegram")
    parser.add_argument("file", help="Путь к .txt файлу")
    parser.add_argument("--token", help="Токен бота")
    parser.add_argument("--chat-id", help="ID чата")
    parser.add_argument("--parse-mode", choices=["HTML", "Markdown", "MarkdownV2"])

    args = parser.parse_args()

    # проверяем файл
    if not Path(args.file).exists():
        print(f"Файл не найден: {args.file}")
        sys.exit(1)

    with open(args.file, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Файл пуст")
        sys.exit(1)

    print(f"Загружено {len(text)} символов")

    # загружаем конфиг и отправляем
    config = load_config(args)
    bot = TelegramBot(config["token"])
    result = bot.send_message(config["chat_id"], text, args.parse_mode)

    if result["success"]:
        print(f"Отправлено! Message ID: {result['message_id']}")
    else:
        print(f"Ошибка: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
