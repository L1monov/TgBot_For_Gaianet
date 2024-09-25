from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode

from TelegramBot.utils.states import FeedBack
from TelegramBot.utils import pagination
from TelegramBot.utils.pagination import Pagination
from TelegramBot.conference_mode.keyboards import inline

from data.async_database import AsyncDataBase, FeedbackDB
from TelegramBot.utils.coincidence import ContainsSubstringFilter

router = Router()


@router.callback_query(ContainsSubstringFilter('find_by_text_'))
async def all_event_2(callback_query: CallbackQuery):
    """
    Handles callback queries related to event searching by text.

    :param callback_query: The callback query from the user
    :return: The message with events matching the search tag and the pagination keyboard
    """
    tag = callback_query.data.split('_')[-1]
    keyboard = await pagination.paginator(tag=tag)
    msg_text = await pagination.get_msg_info_events(tag=tag)
    await callback_query.message.edit_text(text=msg_text['msg_text'], reply_markup=keyboard,
                                           parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


@router.callback_query(Pagination.filter(F.action.in_(['prev', 'next'])))
async def pagination_for_all_list(call: CallbackQuery, callback_data: pagination.Pagination):
    """
    Handles pagination for event lists based on 'next' or 'previous' actions.

    :param call: The callback query object
    :param callback_data: The pagination data
    """
    page_num = int(callback_data.page)
    page = page_num - 1 if page_num > 0 else 0

    if callback_data.action == 'next':
        page = page_num + 1 if page_num < int(callback_data.count_event / 5) else page_num

    msg_text = await pagination.get_msg_info_events(tag=callback_data.tag, skip=page * 5, limit=page * 5 + 5)
    keyboard = await pagination.paginator(page=page, tag=callback_data.tag)
    await call.message.edit_text(text=msg_text['msg_text'], reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN,
                                 disable_web_page_preview=True)


# Feedback Handling

@router.message(F.text == 'FeedBack')
async def feedback(message: Message, state: FSMContext):
    """
    Handles the 'FeedBack' command, prompts the user to write feedback, and sets the feedback state.

    :param message: The user's message object
    :param state: The finite state machine context
    """
    await state.set_state(FeedBack.text_feedback)
    return await message.answer(text='Please write feedback')


@router.message(FeedBack.text_feedback)
async def fill_text_feedback(message: Message, state: FSMContext, bot: Bot):
    """
    Collects user feedback, stores it in the database, and sends the feedback to the admin group.

    :param message: The user's message object
    :param state: The finite state machine context
    :param bot: The bot instance
    """
    await state.update_data(tg_id=message.from_user.id)
    await state.update_data(text_feedback=message.text)
    await state.update_data(username=message.from_user.username)
    data = await state.get_data()

    feedbackdb = FeedbackDB()
    await feedbackdb.add_feedback(username=data['username'], feedback_text=data['text_feedback'], tg_id=data['tg_id'])

    await bot.send_message(chat_id=-1002204713241,
                           text=f"Новый фидбэк от {data['username']}\nСсылка на юзера: https://t.me/{data['username']}\nТекст: {data['text_feedback']}")

    return await message.answer('We have received your message')
