import asyncio
from contextlib import suppress
from aiohttp import web
import os
import requests  # Для отправки уведомлений

from bot.utils.launcher import process


# Имитация простого веб-сервера для Render
async def handle(request):
    return web.Response(text="Bot is running")


async def start_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = os.getenv("PORT", 8000)  # Получаем порт от Render или используем 8000 по умолчанию
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Serving on port {port}")


# Функция для отправки уведомлений через бота
def send_telegram_notification(message):
    bot_token = os.getenv('BOT_TOKEN')  # Токен уведомительного бота из окружения
    chat_id = os.getenv('GROUP_CHAT_ID')  # Телеграм ID группы/канала из окружения

    if not bot_token or not chat_id:
        print("Ошибка: BOT_TOKEN или GROUP_CHAT_ID не установлены.")
        return None

    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}'
    response = requests.get(send_text)
    print(response.status_code, response.json())
    return response.json()


# Периодическая отправка сообщений, чтобы поддерживать активность
async def periodic_activity():
    while True:
        send_telegram_notification("Бот активен и работает.")
        await asyncio.sleep(120)  # Отправляем сообщение каждые 2 минуты (120 секунд)


# Дополнительная "фальшивая" нагрузка
async def fake_load():
    while True:
        await asyncio.sleep(30)  # Пауза в 30 секунд
        requests.get('https://www.google.com')  # Отправка запроса для имитации активности


async def main():
    try:
        send_telegram_notification("Бот успешно запущен на Render!")
        print("Notification sent!")

        # Запускаем веб-сервер, основной код бота и периодическую отправку уведомлений
        await asyncio.gather(
            start_server(),  # Запуск веб-сервера для Render
            process(),  # Основной код твоего бота
            periodic_activity(),  # Периодическая отправка уведомлений
            fake_load()  # Фальшивая нагрузка для имитации активности
        )
    except Exception as e:
        send_telegram_notification(f"Ошибка в работе бота: {e}")
        raise e


if __name__ == '__main__':
    with suppress(KeyboardInterrupt, RuntimeError, RuntimeWarning):
        asyncio.run(main())