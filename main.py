import asyncio
from contextlib import suppress
from aiohttp import web
import os

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


async def main():
    # Запускаем веб-сервер и основного бота параллельно
    await asyncio.gather(
        start_server(),  # Запуск веб-сервера для Render
        process()  # Основной код твоего бота
    )


if __name__ == '__main__':
    with suppress(KeyboardInterrupt, RuntimeError, RuntimeWarning):
        asyncio.run(main())
