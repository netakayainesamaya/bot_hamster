import asyncio
from contextlib import suppress
from aiohttp import web
import os
import aiohttp  # для keep-alive

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

# Функция для периодического отправления keep-alive запросов
async def keep_alive():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8000') as resp:  # Отправляем запрос на локальный сервер
                    print("Keep-alive request sent. Response status:", resp.status)
        except Exception as e:
            print("Failed to send keep-alive request:", str(e))
        await asyncio.sleep(600)  # Интервал в секундах (каждые 10 минут)

async def main():
    # Запуск веб-сервера для удовлетворения требований Render
    await start_server()

    # Параллельно с процессом бота запускаем keep-alive запросы
    await asyncio.gather(
        process(),
        keep_alive()
    )

if __name__ == '__main__':
    with suppress(KeyboardInterrupt, RuntimeError, RuntimeWarning):
        asyncio.run(main())