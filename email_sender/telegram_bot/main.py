import asyncio

from telegram_bot.config.bot_configuration import EmailReaderBot


async def main():
    await EmailReaderBot().run()


if __name__ == "__main__":
    asyncio.run(main())
