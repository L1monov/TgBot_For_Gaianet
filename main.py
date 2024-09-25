import asyncio
from TelegramBot import bot
from data.async_database import check_tables

async def main():
    """
    Main function to start the bot after ensuring that the necessary database tables are set up.
    It first checks and creates tables if they do not exist, then runs the bot.
    """
    await check_tables()  # Ensure tables are created
    await bot.main()  # Run bot

if __name__ == '__main__':
    """
    Entry point for running the bot.
    """
    asyncio.run(main())
