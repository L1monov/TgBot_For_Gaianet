from typing import List, Union, Dict, AnyStr
import json
from datetime import datetime
import asyncio

import aiomysql

from TelegramBot.settings.config import DB_LOGIN, DB_PASSWORD, DB_PORT, DB_HOST, DB_NAME


class AsyncDataBase:

    def __init__(self):
        self.pool = None

    async def init(self):
        if not self.pool:
            self.pool = await aiomysql.create_pool(
                host=DB_HOST,
                port=int(DB_PORT),
                user=DB_LOGIN,
                password=DB_PASSWORD,
                db=DB_NAME,
                cursorclass=aiomysql.DictCursor,
            )

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def execute_query_for_gpt(self, query: str):
        await self.init()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                result = await cursor.fetchall()
                return result

    async def execute_query(self, query: str, args: tuple = ()) -> Union[None, List]:
        await self.init()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, args)
                await conn.commit()
                result = await cursor.fetchall()
                return result

    async def init_tables(self):
        """
        Initializes database tables if they do not exist.

        This function creates several tables for the bot's database:
        1. Users table - stores user information such as Telegram username, ID, preferences, etc.
        2. Conference events table - stores details about conference events including URL, name, description, and more.
        3. Logs table - stores logs of bot interactions including user messages, bot responses, and errors.
        4. Feedback table - stores user feedback with timestamp and user information.

        :return: None
        """

        # SQL query to create the 'users' table if it doesn't exist
        user_tables = """CREATE TABLE if not exists `users` (
                            id_user INT PRIMARY KEY AUTO_INCREMENT,  -- Unique user ID
                            tg_username VARCHAR(32),  -- Telegram username, limited to 32 characters
                            tg_id VARCHAR(20),  -- Telegram ID, limited to 20 characters
                            topics VARCHAR(255),  -- Preferred topics for the user
                            template INT,  -- Template preference (as an integer)
                            timezone INT,  -- Timezone preference (as an integer)
                            type_image VARCHAR(50),  -- Preferred image type, up to 50 characters
                            mode_chat VARCHAR(50) DEFAULT 'news'  -- Default chat mode, can be changed
                        )"""

        # SQL query to create the 'conference_events' table if it doesn't exist
        table_conference = """CREATE TABLE IF NOT EXISTS `conference_events` (
                                id_event INT PRIMARY KEY AUTO_INCREMENT,  -- Unique event ID
                                url_event VARCHAR(255),  -- Event URL (up to 255 characters)
                                name_event VARCHAR(100),  -- Event name (up to 100 characters)
                                date_event VARCHAR(50),  -- Event date in any format (up to 50 characters)
                                location_event VARCHAR(255),  -- Event location (up to 255 characters)
                                description_event LONGTEXT,  -- Detailed event description (can be long)
                                host_event VARCHAR(100),  -- Event host name (up to 100 characters)
                                speakers_event VARCHAR(255),  -- Event speakers (up to 255 characters)
                                tags_event VARCHAR(255),  -- Event tags (up to 255 characters)
                                sponsors VARCHAR(255),  -- Event sponsors (up to 255 characters)
                                urls_in_event VARCHAR(255),  -- Additional event-related URLs (up to 255 characters)
                                agenda LONGTEXT,  -- Detailed agenda (can be long)
                                html_event LONGTEXT  -- Event HTML content (can be long)
                            )"""

        # SQL query to create the 'logs' table if it doesn't exist
        logs_table = """CREATE TABLE IF NOT EXISTS `logs` (
                        id_log INT PRIMARY KEY AUTO_INCREMENT,  -- Unique log ID
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Log timestamp (auto-generated)
                        user_id VARCHAR(255),  -- User ID (up to 255 characters)
                        username VARCHAR(255),  -- Username (up to 255 characters)
                        message_text TEXT,  -- User message text (can be long)
                        response_text TEXT,  -- Bot response text (can be long)
                        error_message TEXT  -- Error message (if any, can be long)
                    )"""

        # SQL query to create the 'feedback' table if it doesn't exist
        feedback_table = """CREATE TABLE IF NOT EXISTS `feedback` (
                                id_feedback INT PRIMARY KEY AUTO_INCREMENT,  -- Unique feedback ID
                                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Feedback timestamp (auto-generated)
                                user_id VARCHAR(255),  -- User ID (up to 255 characters)
                                username VARCHAR(255),  -- Username (up to 255 characters)
                                feedback_text TEXT  -- User feedback text (can be long)
                            )"""

        # List of queries to be executed for table creation
        queries = [user_tables, table_conference, logs_table, feedback_table]

        # Execute each query asynchronously
        for query in queries:
            await self.execute_query(query=query)

    async def log_message(self, user_id: int, username: str, message_text: str, response_text: str, error_message: str):
        query = """INSERT INTO logs (user_id, username, message_text, response_text, error_message)
                   VALUES (%s, %s, %s, %s, %s)"""
        try:
            await self.execute_query(query=query, args=(user_id, username, message_text, response_text, error_message))
        except:
            return

    async def log_news(self, action: str, response: str, error: str, execution_time: str):
        query = """INSERT INTO logs_news (action, response, error, execution_time)
                         VALUES (%s, %s, %s, %s)"""
        args = (action, response, error, execution_time)

        await self.execute_query(query=query, args=args)

    async def log_news_sletter(self, id_news: int, id_tg_user: int, status: str):
        query = """INSERT INTO logs_news_sletter (id_news, id_tg_user, status)
                    values (%s, %s, %s)"""
        args = (id_news, id_tg_user, status)

        await self.execute_query(query=query, args=args)

    async def get_promt(self):
        query = "select text_promt from promt where name_promt = 'main_promt'"
        result = await self.execute_query(query=query)
        return result[0]['text_promt']

    async def get_id_by_tg_id(self, tg_id: int):
        query = 'select id_user from users where tg_id = %s'
        result = await self.execute_query(query=query, args=(tg_id,))
        return result[0]


class UserDB(AsyncDataBase):
    """
    This class handles database operations related to users such as retrieving user data,
    inserting new users, updating settings, and managing user favorite lists.
    """

    async def get_all_users(self):
        """
        Retrieves all users from the 'users' table.

        :return: List of all users
        """
        query = 'select * from users'
        result = await self.execute_query(query=query)
        return result

    async def get_user_info(self, tg_id: int):
        """
        Retrieves user information based on their Telegram ID.

        :param tg_id: Telegram user ID
        :return: User information
        """
        query = "select * from `users` where tg_id = %s"
        return await self.execute_query(query=query, args=(tg_id,))

    async def insert_new_user(self, tg_id: int, tg_username: str) -> None:
        """
        Inserts a new user into the 'users' table if they don't already exist.

        :param tg_id: Telegram user ID
        :param tg_username: Telegram username
        """
        # Check if the user already exists
        check_query = "SELECT COUNT(*) FROM `users` WHERE tg_id = %s"
        insert_query = "INSERT INTO `users` (tg_username, tg_id) VALUES (%s, %s)"

        # Fetch the count of users with the provided Telegram ID
        (count,) = await self.execute_query(check_query, (tg_id,))

        # Insert the new user only if they don't already exist
        if count['COUNT(*)'] == 0:
            await self.execute_query(insert_query, (tg_username, tg_id))

    async def select_all_users(self) -> List[Dict]:
        """
        Retrieves all users from the 'users' table.

        :return: List of users
        """
        query = "select * from `users`"
        return await self.execute_query(query=query)

    # async def add_settins_user(self, data: dict, tg_id: int) -> None:
    #     """
    #     Updates the user's settings in the 'users' table.
    #
    #     :param data: Dictionary containing the user's settings such as topics, template, timezone, and image type
    #     :param tg_id: Telegram user ID
    #     """
    #     query = """update `users` set topics = %s,
    #                                   template = %s,
    #                                   timezone = %s,
    #                                   type_image = %s
    #                                   where tg_id = %s"""
    #     args = (data['list_topics'], data['template'], data['timezone'], data['type_img'], tg_id)
    #     await self.execute_query(query=query, args=args)

    # async def set_mode_user(self, tg_id_user: int, mode_chat: str):
    #     """
    #     Updates the chat mode for a user.
    #
    #     :param tg_id_user: Telegram user ID
    #     :param mode_chat: The new chat mode
    #     """
    #     query = "update `users` set mode_chat = %s where tg_id = %s"
    #     args = (mode_chat, tg_id_user)
    #     await self.execute_query(query=query, args=args)

    # async def edit_topics(self, list_topics: list, tg_id: int):
    #     """
    #     Updates the topics for a user.
    #
    #     :param list_topics: List of topics the user is interested in
    #     :param tg_id: Telegram user ID
    #     """
    #     topics_str = json.dumps(sorted(list_topics))
    #     query = 'update `users` set topics = %s where tg_id = %s'
    #     args = (topics_str, tg_id)
    #     await self.execute_query(query=query, args=args)
    #
    # async def update_settings(self, tg_id_user: int, column_change: str, value: str):
    #     """
    #     Updates a specific column for a user.
    #
    #     :param tg_id_user: Telegram user ID
    #     :param column_change: The column to be updated
    #     :param value: The new value for the column
    #     """
    #     query = f"update users set {column_change} = %s where tg_id = %s"
    #     await self.execute_query(query=query, args=(value, tg_id_user))

    async def get_info_by_id(self, id_user: int):
        """
        Retrieves user information by their user ID.

        :param id_user: User ID
        :return: User information
        """
        query = 'select * from users where id_user = %s'
        args = (id_user,)
        result = await self.execute_query(query=query, args=args)
        return result

    async def add_favorit_private_lists(self, id_user: int, list_id: int):
        """
        Adds a list to the user's favorite private lists.

        :param id_user: User ID
        :param list_id: The list ID to be added
        """
        query = """UPDATE users
                   SET favorites_private_lists = CONCAT(favorites_private_lists, %s)
                   where id_user = %s"""
        args = (f",{list_id}", id_user)
        await self.execute_query(query=query, args=args)

    async def delete_favorit_private_lists(self, id_user: int, list_id: int):
        """
        Removes a list from the user's favorite private lists.

        :param id_user: User ID
        :param list_id: The list ID to be removed
        """
        query = """UPDATE users
                   SET favorites_private_lists = TRIM(BOTH ',' FROM REPLACE(CONCAT(',', TRIM(BOTH ',' FROM favorites_private_lists), ','), CONCAT(',', %s, ','), ','))
                   WHERE id_user = %s"""
        args = (list_id, id_user)
        await self.execute_query(query=query, args=args)

    async def get_favorite_private_list_by_user_id(self, id_user: int):
        """
        Retrieves the favorite private lists for a user by their Telegram ID.

        :param id_user: User ID
        :return: The user's favorite private lists
        """
        query = 'select favorites_private_lists from users where tg_id = %s'
        args = (id_user,)
        result = await self.execute_query(query=query, args=args)
        return result


# class NewDB(AsyncDataBase):
#     """
#     This class handles database operations related to topics, presets, timezones, and templates.
#     It includes methods for retrieving and updating topics, adding new templates, and getting preset information.
#     """
#
#     # Methods related to TOPICS
#     async def get_topics(self) -> List[Dict]:
#         """
#         Retrieves all topics from the 'topics' table.
#
#         :return: List of topics
#         """
#         query = 'select * from topics'
#         return await self.execute_query(query=query)
#
#     async def add_user_topic(self, topics: List[int], tg_id: int) -> None:
#         """
#         Updates the user's topics in the 'users' table.
#
#         :param topics: List of topic IDs
#         :param tg_id: Telegram user ID
#         """
#         query = "update `users` set topics = (%s) where tg_id = (%s)"
#         topics_str = json.dumps(topics)  # Convert the list of topics to a JSON string
#         await self.execute_query(query=query, args=(topics_str, tg_id))
#
#     async def get_presets(self):
#         """
#         Retrieves all presets from the 'presets_topics' table.
#
#         :return: List of presets
#         """
#         query = 'select * from presets_topics'
#         result = await self.execute_query(query=query)
#         return result
#
#     async def get_preset_by_id(self, id_preset: int):
#         """
#         Retrieves a specific preset by its ID from the 'presets_topics' table.
#
#         :param id_preset: Preset ID
#         :return: Preset information
#         """
#         query = 'select * from presets_topics where id_preset = %s'
#         args = (id_preset,)
#         result = await self.execute_query(query=query, args=args)
#         return result[0]
#
#     # Methods related to TIMEZONE
#     async def get_timezone(self):
#         """
#         Retrieves all timezones from the 'timezone' table.
#
#         :return: List of timezones
#         """
#         query = 'select * from `timezone`'
#         return await self.execute_query(query=query)
#
#     async def get_timezone_by_id(self, id_timezone: int):
#         """
#         Retrieves a specific timezone by its ID from the 'timezone' table.
#
#         :param id_timezone: Timezone ID
#         :return: Timezone information
#         """
#         query = "select * from timezone where id_timezone = %s"
#         result = await self.execute_query(query=query, args=(id_timezone,))
#         return result[0]
#
#     # Temporary methods for development purposes
#     async def add_topic(self, name_topic: str) -> None:
#         """
#         Inserts a new topic into the 'topics' table.
#
#         :param name_topic: Name of the topic to be added
#         """
#         query = f"insert into topics (name_topic) values ('{name_topic}')"
#         await self.execute_query(query=query)
#
#     async def get_templates(self) -> List:
#         """
#         Retrieves all templates from the 'templates' table.
#
#         :return: List of templates
#         """
#         query = "select * from templates"
#         result = await self.execute_query(query=query)
#         return result
#
#     async def get_template_by_id(self, id_template: int):
#         """
#         Retrieves a specific template by its ID from the 'templates' table.
#
#         :param id_template: Template ID
#         :return: Template information
#         """
#         query = 'select * from templates where id_template = %s'
#         result = await self.execute_query(query=query, args=(id_template,))
#         return result[0]
#
#     async def add_template(self, name_template: str, about_template: str) -> None:
#         """
#         Inserts a new template into the 'templates' table.
#
#         :param name_template: Name of the template
#         :param about_template: Description of the template
#         """
#         query = f"insert into templates (name_template, about_template) values ('{name_template}', '{about_template}')"
#         await self.execute_query(query=query)
#
#     async def add_timezone(self, time: datetime, name_timezone: str) -> None:
#         """
#         Inserts a new timezone into the 'timezone' table.
#
#         :param time: UTC time for the timezone
#         :param name_timezone: Name of the timezone
#         """
#         query = f"insert into timezone (time_utc, name_timezone) values ({time}, '{name_timezone}')"
#         await self.execute_query(query=query)
#
#     async def get_info_settings_news_mode(self, tg_id):
#         """
#         Retrieves user settings including preset, template, timezone, and image type for the news mode.
#
#         :param tg_id: Telegram user ID
#         :return: Dictionary containing user's preset, template, timezone, and image type
#         """
#         query = 'select * from users where tg_id = %s'
#         result = await self.execute_query(query=query, args=(tg_id,))
#         info_user = result[0]
#
#         # Retrieve preset information based on the user's selected topics
#         preset_query = "select * from presets_topics where id_preset = %s"
#         result_preset = await self.execute_query(query=preset_query, args=(info_user['topics'],))
#         preset = result_preset[0]['name']
#
#         # Retrieve template information based on the user's selected template
#         template_query = 'select * from templates where id_template = %s'
#         result_template = await self.execute_query(query=template_query, args=(info_user['template'],))
#         template = result_template[0]['name_template']
#
#         # Retrieve timezone information based on the user's selected timezone
#         timezone_query = 'select * from timezone where id_timezone = %s'
#         result_timezone = await self.execute_query(query=timezone_query, args=(info_user['timezone'],))
#         timezone = result_timezone[0]['name_timezone']
#
#         # Return a dictionary with the user's preset, template, timezone, and image type
#         return {'preset': preset, 'template': template, 'timezone': timezone, 'type_image': info_user['type_image']}


class AdminDB(AsyncDataBase):
    """
    This class handles administrative database operations such as retrieving user counts
    and calculating the average number of requests per user.
    """

    async def get_count_user(self):
        """
        Retrieves the total number of users from the 'users' table.

        :return: Total number of users
        """
        query = 'select count(*) as count_user from `users`'
        result = await self.execute_query(query=query)
        return result[0]['count_user']  # Return the user count from the result

    async def get_average_requests_users(self):
        """
        Calculates the average number of requests made by users based on log entries.

        This method groups logs by user, counts the number of requests made by each user,
        and then calculates the average number of requests.

        :return: Average number of requests per user (rounded to an integer)
        """
        query = 'select count(*) as count_requst, user_id, username from logs group by user_id'
        result = await self.execute_query(query=query)

        # Calculate the total number of requests
        total_requests = sum(user['count_requst'] for user in result)

        # Calculate the average by dividing total requests by the number of users
        average_requests = total_requests / len(result)

        return int(average_requests)  # Return the average as an integer


class Event(AsyncDataBase):
    """
    This class handles database operations related to conference events. It includes methods
    to retrieve, update, and search for events by different criteria such as tags, location, and date.
    """

    async def get_all_events(self):
        """
        Retrieves all events from the 'conference_events' table.

        :return: List of all events
        """
        query = 'select * from conference_events'
        result = await self.execute_query(query=query)
        return result

    async def update_info(self, url_event: str, column: str, value: str):
        """
        Updates a specific column for an event identified by its URL.

        :param url_event: URL of the event
        :param column: Column name to be updated
        :param value: New value for the column
        """
        query = f"UPDATE conference_events SET {column} = %s WHERE url_event = %s"
        args = (value, url_event)
        await self.execute_query(query=query, args=args)

    async def update_info_by_name(self, name_event: str, column: str, value: str):
        """
        Updates a specific column for an event identified by its name.

        :param name_event: Name of the event
        :param column: Column name to be updated
        :param value: New value for the column
        """
        query = f"UPDATE conference_events SET {column} = %s where name_event = %s"
        args = (value, name_event)
        await self.execute_query(query=query, args=args)

    async def get_all_urls_events(self):
        """
        Retrieves the URLs of all events from the 'conference_events' table.

        :return: List of event URLs
        """
        query = 'select url_event from conference_events'
        result = await self.execute_query(query=query)
        list_urls = [event['url_event'] for event in result]
        return list_urls

    async def get_info_all_events_by_tag(self, tag: str):
        """
        Retrieves basic information (name, date, time, URL) for all events that match a specific tag.

        :param tag: Tag to search for
        :return: List of events that match the tag
        """
        query = 'select name_event, date_event, time_event, url_event from conference_events where LOWER(tags_event) like LOWER(%s) and name_event not like %s'
        args = (f"%{tag}%", '%EthCC Main Event:%')
        return await self.execute_query(query=query, args=args)

    async def get_info_many_events(self, list_ids_events: list):
        """
        Retrieves detailed information for multiple events based on their IDs.

        :param list_ids_events: List of event IDs
        :return: List of events with detailed information
        """
        query = 'select * from conference_events where id_event in %s'
        args = (set(list_ids_events),)
        result = await self.execute_query(query=query, args=args)
        return result

    async def get_info_event_by_id(self, id_event: int):
        """
        Retrieves detailed information for a specific event based on its ID.

        :param id_event: Event ID
        :return: Event details
        """
        query = 'select * from conference_events where id_event = %s'
        args = (id_event,)
        result = await self.execute_query(query=query, args=args)
        print('result', result)  # For debugging purposes
        return result[0]

    async def find_events_by_tag(self, tags: list):
        """
        Finds events that match any of the provided tags.

        If 'AI' is among the tags, a special query is used. Otherwise, a general query is constructed
        to search for events with any of the specified tags.

        :param tags: List of tags to search for
        :return: List of events that match the tags
        """
        if 'AI' in tags:
            query = "SELECT * FROM conference_events WHERE tags_event LIKE %s"
            params = ("%, AI%",)
        else:
            query = 'select * from conference_events where '
            query += " or ".join(["tags_event like %s" for _ in tags])
            params = [f"%{tag}%" if tag != 'Sport' else tag for tag in tags]

        print(query, params)  # For debugging purposes
        result = await self.execute_query(query=query, args=params)
        return result

    async def main_events_find_by_location(self, location: str):
        """
        Finds main events (events with names like '[IMPACT]') by location.

        :param location: Location to search for
        :return: List of events in the specified location
        """
        query = "select * from conference_events where name_event like %s and location_event like %s"
        args = ("%[IMPACT]%", f"%{location}%")
        result = await self.execute_query(query=query, args=args)
        return result

    async def main_events_find_by_day(self, day: str):
        """
        Finds main events (events with names like '[IMPACT]') by day.

        :param day: Day to search for (formatted as a string)
        :return: List of events on the specified day
        """
        query = "select * from conference_events where name_event like %s and date_event like %s"
        args = ("%[IMPACT]%", f"%{day}%")
        result = await self.execute_query(query=query, args=args)
        return result

    async def main_events_find_by_location_and_day(self, location: str, day: str):
        """
        Finds main events (events with names like '[IMPACT]') by both location and day.

        :param location: Location to search for
        :param day: Day to search for
        :return: List of events that match both location and day
        """
        query = "select * from conference_events where name_event like %s and date_event like %s and location_event like %s"
        args = ("%[IMPACT]%", f"%{day}%", f"%{location}%")
        result = await self.execute_query(query=query, args=args)
        return result


class LogsDB(AsyncDataBase):
    """
    This class handles logging operations for the bot. It logs user messages, bot responses, and errors into the 'logs' table.
    """

    async def log_message(self, user_id: int, username: str, message_text: str, response_text: str, error_message: str):
        """
        Logs a message from the user, the bot's response, and any error encountered into the 'logs' table.

        :param user_id: Telegram user ID
        :param username: Username of the user
        :param message_text: Message sent by the user
        :param response_text: Response generated by the bot
        :param error_message: Error message, if any, encountered during processing
        """
        query = """INSERT INTO logs (user_id, username, message_text, response_text, error_message)
                   VALUES (%s, %s, %s, %s, %s)"""
        try:
            # Executes the query asynchronously with the provided arguments
            await self.execute_query(query=query, args=(user_id, username, message_text, response_text, error_message))
        except:
            # If any error occurs during the logging process, it is silently handled
            return


class FeedbackDB(AsyncDataBase):
    """
    This class handles feedback-related operations, such as adding user feedback to the database.
    """

    async def add_feedback(self, username: str, tg_id: int, feedback_text: str):
        """
        Adds a user's feedback to the 'feedback' table in the database.

        :param username: Username of the user providing feedback
        :param tg_id: Telegram user ID
        :param feedback_text: The feedback text provided by the user
        """
        query = '''insert into `feedback` (user_id, username, feedback_text)
                    values (%s, %s, %s)'''
        args = (tg_id, username, feedback_text)

        # Executes the query asynchronously to insert the feedback into the database
        await self.execute_query(query=query, args=args)


class ParsingDB(AsyncDataBase):
    """
    This class handles operations related to parsing and fetching event data from the 'conference_events' table.
    It includes methods for retrieving recently added or updated events, as well as getting event counts.
    """

    async def get_last_add_events(self, hours: int):
        """
        Retrieves all events that were added within the last specified number of hours.

        :param hours: The number of hours to look back for recently added events
        :return: List of events added in the specified time range
        """
        query = f"""SELECT *
                    FROM conference_events
                    WHERE date_add >= NOW() - INTERVAL {hours} HOUR;
                 """
        result = await self.execute_query(query=query)
        return result

    async def get_count_events(self):
        """
        Retrieves the total count of events in the 'conference_events' table.

        :return: Total number of events
        """
        query = 'select count(*) from conference_events'
        result = await self.execute_query(query=query)
        return result[0]['count(*)']  # Return the count of events from the result

    async def get_last_update_event(self, hours: int):
        """
        Retrieves all events that were updated within the last specified number of hours,
        and whose 'type_update' field matches '%update%'.

        :param hours: The number of hours to look back for recently updated events
        :return: List of updated events in the specified time range
        """
        query = 'select * from conference_events where type_update like %s and date_update >= NOW() - INTERVAL %s HOUR'
        result = await self.execute_query(query=query, args=("%update%", hours,))
        return result


class ListEvents(AsyncDataBase):
    """
    This class handles the creation, management, and retrieval of both private and public event lists for users.
    It includes methods to create lists, add or remove events from lists, and retrieve lists by user or secret key.
    """

    # Methods related to creating lists
    async def create_private_list(self, tg_user: int, username: str):
        """
        Creates a private event list for the user. The list is associated with the user's ID and a unique key.

        :param tg_user: Telegram user ID
        :param username: Username of the user (default to 'None' if username is not provided)
        """
        if username is None:
            username = 'None'
        id_user_in_db = await self.get_id_by_tg_id(tg_id=tg_user)
        id_user_in_db = id_user_in_db['id_user']
        query = 'insert into private_list_events (`key`, id_user, name_list) values (%s, %s, %s)'
        key = f'{str(tg_user)[5:]}'  # Generate a key based on the Telegram user ID
        args = (key, id_user_in_db, f"Priv_{username}")
        await self.execute_query(query=query, args=args)

    async def create_public_list(self, tg_user: int, username: str):
        """
        Creates a public event list for the user. The list is associated with the user's ID and a unique key.

        :param tg_user: Telegram user ID
        :param username: Username of the user (default to 'None' if username is not provided)
        """
        if username is None:
            username = 'None'
        id_user_in_db = await self.get_id_by_tg_id(tg_id=tg_user)
        id_user_in_db = id_user_in_db['id_user']
        query = 'insert into public_list_events (`key`, id_user, name_list) values (%s, %s, %s)'
        key = f'{str(tg_user)[5:]}'  # Generate a key based on the Telegram user ID
        args = (key, id_user_in_db, f"Pub_{username}")
        await self.execute_query(query=query, args=args)

    async def check_private_list_user_and_create_if_none(self, tg_id_user: int, username: str):
        """
        Checks if the user has a private event list. If not, creates one.

        :param tg_id_user: Telegram user ID
        :param username: Username of the user
        """
        id_user_in_db = await self.get_id_by_tg_id(tg_id=tg_id_user)
        id_user_in_db = id_user_in_db['id_user']

        # Check if the user already has a private list
        result = await self.execute_query(query=f'select * from private_list_events where id_user = {id_user_in_db}')
        if result:
            print('Already created list')
        else:
            await self.create_private_list(tg_user=tg_id_user, username=username)

        # Check if the user already has a public list
        result = await self.execute_query(query=f'select * from public_list_events where id_user = {id_user_in_db}')
        if result:
            print('Already created list')
        else:
            await self.create_public_list(tg_user=tg_id_user, username=username)

    async def get_lists_user_by_tg_id(self, tg_id: int):
        """
        Retrieves both public and private event lists for a user by their Telegram ID.

        :param tg_id: Telegram user ID
        :return: List of private and public event lists for the user
        """
        user_id = await self.get_id_by_tg_id(tg_id=tg_id)
        user_id = user_id['id_user']

        private_lists = 'select * from private_list_events where id_user = %s'
        result_private_lists = await self.execute_query(query=private_lists, args=(user_id,))
        return result_private_lists

    # Methods for adding and removing events from lists
    async def add_event_in_private_list(self, id_event: int, id_list: int):
        """
        Adds an event to a user's private list by concatenating event IDs.

        :param id_event: Event ID to be added
        :param id_list: List ID where the event should be added
        """
        query = """UPDATE private_list_events
                   SET event_ids = CONCAT(event_ids, %s)
                   where id_list = %s"""
        args = (f",{id_event}", id_list)
        print(query)  # For debugging purposes
        print(args)  # For debugging purposes
        await self.execute_query(query=query, args=args)

    async def add_event_in_public_list(self, id_event: int, id_list: int):
        """
        Adds an event to a user's public list by concatenating event IDs.

        :param id_event: Event ID to be added
        :param id_list: List ID where the event should be added
        """
        query = """UPDATE public_list_events
                   SET event_ids = CONCAT(event_ids, %s)
                   where id_list = %s"""
        args = (f",{id_event}", id_list)
        await self.execute_query(query=query, args=args)

    async def remove_event_from_public_list(self, id_event: int, id_list: int):
        """
        Removes an event from a user's public list by trimming event IDs.

        :param id_event: Event ID to be removed
        :param id_list: List ID from which the event should be removed
        """
        query = """UPDATE public_list_events
                   SET event_ids = TRIM(BOTH ',' FROM REPLACE(CONCAT(',', TRIM(BOTH ',' FROM event_ids), ','), CONCAT(',', %s, ','), ','))
                   WHERE id_list = %s"""
        args = (id_event, id_list)
        await self.execute_query(query=query, args=args)

    async def remove_event_from_private_list(self, id_event: int, id_list: int):
        """
        Removes an event from a user's private list by trimming event IDs.

        :param id_event: Event ID to be removed
        :param id_list: List ID from which the event should be removed
        """
        query = """UPDATE private_list_events
                   SET event_ids = TRIM(BOTH ',' FROM REPLACE(CONCAT(',', TRIM(BOTH ',' FROM event_ids), ','), CONCAT(',', %s, ','), ','))
                   WHERE id_list = %s"""
        args = (id_event, id_list)
        await self.execute_query(query=query, args=args)

    # Methods for retrieving lists
    async def get_privete_lists_events_by_tg_id(self, tg_id_user: int):
        """
        Retrieves all private event lists for a user by their Telegram ID.

        :param tg_id_user: Telegram user ID
        :return: List of private event lists for the user
        """
        id_user = await self.get_id_by_tg_id(tg_id=tg_id_user)
        id_user = id_user['id_user']

        query = 'select * from private_list_events where id_user = %s'
        args = (id_user,)
        result = await self.execute_query(query=query, args=args)
        return result

    async def get_public_lists_events_by_tg_id(self, tg_id_user: int):
        """
        Retrieves all public event lists for a user by their Telegram ID.

        :param tg_id_user: Telegram user ID
        :return: List of public event lists for the user
        """
        id_user = await self.get_lists_user_by_tg_id(tg_id=tg_id_user)
        id_user = id_user['id_user']

        query = 'select * from private_list_events where id_user = %s'
        args = (id_user,)
        result = await self.execute_query(query=query, args=args)
        return result

    async def get_list_event_ids_by_id_list(self, id_list: int, type_list: str):
        """
        Retrieves the event IDs from a list based on the list's ID and type (private or public).

        :param id_list: List ID
        :param type_list: Type of list (either 'private' or 'public')
        :return: Event IDs from the specified list
        """
        query = f"select event_ids from {type_list}_list_events where id_list = %s"
        args = (id_list,)
        result = await self.execute_query(query=query, args=args)
        return result

    async def get_list_by_secret_key(self, key: int):
        """
        Retrieves a private event list based on a secret key.

        :param key: Secret key associated with the list
        :return: Private event list matching the secret key
        """
        query = 'select * from private_list_events where `key` = %s'
        args = (int(key),)
        result = await self.execute_query(query=query, args=args)
        return result

    async def get_all_private_lists(self):
        """
        Retrieves all private event lists.

        :return: List of all private event lists
        """
        query = 'select * from private_list_events'
        result = await self.execute_query(query=query)
        return result

    async def get_info_user_by_list_id(self, id_list: int):
        """
        Retrieves user information based on the list ID from a private event list.

        :param id_list: List ID
        :return: User information for the list owner
        """
        info_list = 'select * from private_list_events where id_list = %s'
        info_list = await self.execute_query(query=info_list, args=(id_list,))
        info_user = 'select * from users where id_user = %s'
        info_user = await self.execute_query(query=info_user, args=(info_list[0]['id_user'],))
        return info_user

async def check_tables():
    db = AsyncDataBase()
    await db.init_tables()