from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


async def keyboard_for_updated_events():
    """
    Creates an inline keyboard with a button to show updated events.

    :return: InlineKeyboardMarkup with 'Show updated events' button
    """
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Show updated events', callback_data='view_about_updated_events'))
    return builder.as_markup()
