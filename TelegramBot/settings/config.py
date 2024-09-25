import dotenv
import os

dotenv.load_dotenv()

# Load environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_LOGIN = os.getenv("DB_LOGIN")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv('DB_NAME')
ADMINS_IDS = [int(num) for num in os.getenv('ADMINS_IDS', '').split(',') if num.isdigit()]
GROUP_FOR_SUBCRIPTION = int(os.getenv('GROUP_FOR_SUBSCRIPTION'))
NEWS_USERNAME = os.getenv('NEWS_USERNAME')
NEWS_PASSWORD = os.getenv('NEWS_PASSWORD')
GAIANET_URL = os.getenv('GAIANET_URL')

def get_url_database():
    """
    Constructs the URL for connecting to the MySQL database using the environment variables.

    :return: The constructed MySQL database URL.
    """
    url = f'mysql://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    return url
