from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


async def select_day_main_event():
    """
    Creates an inline keyboard to select a day for the main event.

    :return: InlineKeyboardMarkup for selecting a day
    """
    builder = InlineKeyboardBuilder()
    builder.button(text='8 July', callback_data='maineventsetday_8*July')
    builder.button(text='9 July', callback_data='maineventsetday_9*July')
    builder.button(text='10 July', callback_data='maineventsetday_10*July')
    builder.button(text='11 July', callback_data='maineventsetday_11*July')

    builder.button(text='--', callback_data='None')
    builder.button(text='--', callback_data='None')

    list_topics = ['Gaming', 'ZK', 'VC', 'Security', 'Regulation', 'AI']
    for topic in list_topics:
        builder.button(text=topic, callback_data=f'maineventsettopic_{topic}')

    builder.adjust(2)
    return builder.as_markup()


async def select_location_main_event():
    """
    Creates an inline keyboard to select a location for the main event.

    :return: InlineKeyboardMarkup for selecting a location
    """
    builder = InlineKeyboardBuilder()
    list_location = ['Gold Hall', 'Silver Hall', 'Hankar Stage', 'Copper Hall', 'Harta Stage', 'Warcraft Stage',
                     'Strauven Stage', 'EthVC Stage']
    for location in list_location:
        builder.button(text=location, callback_data=f"maineventsetlocation_{location}")
    builder.adjust(2)
    return builder.as_markup()


async def select_topic_main_event():
    """
    Creates an empty inline keyboard for selecting a topic for the main event.

    :return: InlineKeyboardMarkup for selecting a topic
    """
    builder = InlineKeyboardBuilder()
    builder.adjust(2)
    return builder.as_markup()


async def keyboard_for_all_event_select_tag():
    """
    Creates an inline keyboard to select tags for filtering events.

    :return: InlineKeyboardMarkup for selecting event tags
    """
    tags = ['zk', 'ai', 'vc', 'breakfast', 'food', 'drinks', 'party', 'hacker', 'sport', 'coworking']
    builder = InlineKeyboardBuilder()
    for tag in tags:
        builder.add(InlineKeyboardButton(text=tag, callback_data=f'find_by_text_{tag}'))
    builder.adjust(2)
    return builder.as_markup()
