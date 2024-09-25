from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import KeyboardButton

from data.async_database import ListEvents

ListEventsDb = ListEvents()


async def main_keyboard_conference_mode():
    """
    Creates the main keyboard for the conference mode.

    :return: ReplyKeyboardMarkup with main conference options
    """
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='🗂️My Events'))
    builder.add(KeyboardButton(text='📜Side Events'))
    builder.add(KeyboardButton(text='📖Categories'))
    builder.add(KeyboardButton(text='🔎Find list'))
    builder.add(KeyboardButton(text='📜Main Event Agenda'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

async def keyboard_for_view_extended_info_events(list_events: list, str_list_ids_event: str, pagination: bool = True):
    """
    Creates an inline keyboard for viewing extended event information.

    :param list_events: List of events
    :param str_list_ids_event: String of event IDs
    :param pagination: Boolean to enable pagination (default: True)
    :return: InlineKeyboardMarkup for viewing extended info of events
    """
    builder = InlineKeyboardBuilder()
    for event in list_events:
        builder.add(InlineKeyboardButton(text=str(event['id_pagination']),
                                         callback_data=f'view_extened_info_event_{event["id_event"]}'))
    if pagination:
        # Add pagination logic if needed
        pass
    return builder.as_markup()


async def keyboard_for_add_or_remove_event(id_event: int, tg_id: int):
    """
    Creates an inline keyboard for adding or removing an event from the user's list.

    :param id_event: Event ID
    :param tg_id: Telegram user ID
    :return: InlineKeyboardMarkup with add/remove options
    """
    builder = InlineKeyboardBuilder()
    lists_user = await ListEventsDb.get_lists_user_by_tg_id(tg_id=tg_id)
    text = 'Event Removed ☑️'
    callback = f"add_event_in_list_{id_event}*{lists_user[0]['id_list']}_Priv"
    if str(id_event) in lists_user[0]['event_ids'].split(','):
        text = 'Event saved ✅'
        callback = f"remove_event_in_list_{id_event}*{lists_user[0]['id_list']}_Priv"
    builder.add(InlineKeyboardButton(text=text, callback_data=callback))
    builder.add(InlineKeyboardButton(text='Back to list', callback_data='back_to_list_events'))
    builder.adjust(1)
    return builder.as_markup()


async def keyboard_choice_for_add_in_list(id_event: int, tg_id: int):
    """
    Creates an inline keyboard for choosing whether to save or remove an event from the user's private list.

    :param id_event: Event ID
    :param tg_id: Telegram user ID
    :return: InlineKeyboardMarkup with options for private list management
    """
    builder = InlineKeyboardBuilder()
    lists_user = await ListEventsDb.get_lists_user_by_tg_id(tg_id=tg_id)
    text = 'Save to Private list'
    callback = f"add_event_in_list_{id_event}*{lists_user[0]['id_list']}_Priv"
    if str(id_event) in lists_user[0]['event_ids'].split(','):
        text = 'Remove from Private list'
        callback = f"remove_event_in_list_{id_event}*{lists_user[0]['id_list']}_Priv"
    builder.add(InlineKeyboardButton(text=text, callback_data=callback))
    builder.add(InlineKeyboardButton(text='Back to list', callback_data='back_to_list_events'))
    builder.adjust(1)
    return builder.as_markup()


async def keyboard_show_lists(list_dict: dict):
    """
    Creates an inline keyboard to display the user's event lists (private/public).

    :param list_dict: Dictionary of event lists
    :return: InlineKeyboardMarkup for selecting event lists
    """
    builder = InlineKeyboardBuilder()
    for list_event in list_dict:
        builder.add(InlineKeyboardButton(text=list_event['name_list'].replace('Priv_', '').replace('Pub_', ''),
                                         callback_data=f'show_info_list_{list_event["id_list"]}*{"Priv" if "Priv_" in list_event["name_list"] else "Pub"}'))
    builder.adjust(2)
    return builder.as_markup()


# OLD
async def create_builder_reply(text: str | list, max_buttons_in_line: int = 1):
    """
    Creates a reply keyboard from a list of text options.

    :param text: A string or list of button texts
    :param max_buttons_in_line: Maximum number of buttons per row
    :return: ReplyKeyboardMarkup
    """
    if isinstance(text, str):
        text = [text]
    builder = ReplyKeyboardBuilder()
    [builder.add(KeyboardButton(text=txt)) for txt in text]
    builder.adjust(max_buttons_in_line)
    return builder.as_markup(resize_keyboard=True)


async def keyboard_main_menu_reply():
    """
    Creates a reply keyboard for the main menu.

    :return: ReplyKeyboardMarkup with main menu options
    """
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='🗺️EthCC Main Event'))
    builder.add(KeyboardButton(text='📃Side events'))
    builder.add(KeyboardButton(text='FeedBack'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


async def keyboard_main_menu_inline():
    """
    Creates an inline keyboard for the main menu.

    :return: InlineKeyboardMarkup with main menu options
    """
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='🗺️EthCC Main Event', callback_data='EthCC Main Event'))
    builder.add(InlineKeyboardButton(text='📃Side events', callback_data='Side events'))
    builder.adjust(2)
    return builder.as_markup()


async def admin_keyboard():
    """
    Creates a reply keyboard for admin actions.

    :return: ReplyKeyboardMarkup with admin options
    """
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Count users'))
    builder.add(KeyboardButton(text='Agerage request'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def keyboard_check_subscription():
    """
    Creates an inline keyboard to check subscription status.

    :return: InlineKeyboardMarkup for subscription status
    """
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Subscribed', callback_data='check_subcription')
    return builder.as_markup()


async def events_by_tag():
    """
    Creates an inline keyboard for selecting events by tag.

    :return: InlineKeyboardMarkup for tag-based event selection
    """
    builder = InlineKeyboardBuilder()
    tags_dict = {'Official Event': 'Official',
                 'AI': 'AI',
                 'Gaming': 'Gaming-Esport',
                 'Party': 'Night-Party',
                 'Drinks': 'Drinks',
                 'Sport': 'Sport-Run-CrossFit-Yoga'}

    for tag in tags_dict:
        builder.add(InlineKeyboardButton(text=tag, callback_data=f'find_events_by_tag_{tags_dict[tag]}'))
    builder.adjust(2)
    return builder.as_markup()
