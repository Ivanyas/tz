#!/usr/bin/env python3
"""
Проверка email: MX-записи + SMTP handshake

Запуск:
    python email_verifier.py emails.txt
    python email_verifier.py --email user@example.com
"""

import sys
import re
import dns.resolver
import smtplib
import socket


class EmailVerifier:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.from_email = "verify@example.com"

    def verify(self, email):
        # проверка формата
        if not self._is_valid_format(email):
            return {"email": email, "status": "невалидный формат email"}

        domain = email.split("@")[1]

        # проверка MX-записей
        mx_host = self._get_mx_record(domain)
        if not mx_host:
            return {"email": email, "status": "MX-записи отсутствуют или некорректны"}

        # SMTP handshake
        return self._smtp_verify(email, mx_host)

    def _is_valid_format(self, email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def _get_mx_record(self, domain):
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            # берём запись с наименьшим приоритетом
            best_mx = min(mx_records, key=lambda x: x.preference)
            return str(best_mx.exchange).rstrip(".")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.resolver.NoAnswer):
            return None
        except Exception:
            return None

    def _smtp_verify(self, email, mx_host):
        result = {
            "email": email,
            "mx_host": mx_host,
        }

        try:
            smtp = smtplib.SMTP(timeout=self.timeout)
            smtp.connect(mx_host, 25)
            smtp.helo("verify.local")
            smtp.mail(self.from_email)

            # RCPT TO — проверяем существует ли получатель
            code, message = smtp.rcpt(email)
            smtp.quit()

            result["smtp_code"] = code

            if code == 250:
                result["status"] = "домен валиден"
                result["details"] = "пользователь существует"
            elif code == 550:
                result["status"] = "пользователь не существует"
                result["details"] = message.decode()
            else:
                result["status"] = "домен валиден"
                result["details"] = f"неопределённый ответ: {message.decode()}"

        except smtplib.SMTPServerDisconnected:
            result["status"] = "домен валиден"
            result["details"] = "сервер закрыл соединение (greylisting или защита)"
        except socket.timeout:
            result["status"] = "домен валиден"
            result["details"] = "таймаут соединения"
        except ConnectionRefusedError:
            result["status"] = "домен отсутствует"
            result["details"] = "соединение отклонено"
        except Exception as e:
            result["status"] = "домен валиден"
            result["details"] = f"ошибка: {str(e)}"

        return result


def print_result(result):
    print(f"\nEmail: {result['email']}")
    print(f"  Статус: {result['status']}")
    if result.get("mx_host"):
        print(f"  MX-сервер: {result['mx_host']}")
    if result.get("smtp_code"):
        print(f"  SMTP-код: {result['smtp_code']}")
    if result.get("details"):
        print(f"  Детали: {result['details']}")


def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python email_verifier.py emails.txt")
        print("  python email_verifier.py --email user@example.com")
        sys.exit(1)

    emails = []

    if sys.argv[1] == "--email":
        if len(sys.argv) < 3:
            print("Укажите email после --email")
            sys.exit(1)
        emails = [sys.argv[2]]
    else:
        filename = sys.argv[1]
        try:
            with open(filename, "r") as f:
                emails = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Файл {filename} не найден")
            sys.exit(1)

    if not emails:
        print("Список email пуст")
        sys.exit(1)

    verifier = EmailVerifier()

    print("\n" + "=" * 50)
    print("ПРОВЕРКА EMAIL")
    print("=" * 50)

    for email in emails:
        print(f"\nПроверяю: {email}...", end=" ", flush=True)
        result = verifier.verify(email)
        print(f"[{result['status']}]")
        print_result(result)


if __name__ == "__main__":
    main()
