from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


async def keyboard_for_view_all_new_events():
    """
    Creates an inline keyboard with a button to show new events.

    :return: InlineKeyboardMarkup with 'Show new events' button
    """
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Show new events', callback_data='view_about_new_events'))
    return builder.as_markup()
