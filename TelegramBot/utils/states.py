from aiogram.fsm.state import StatesGroup, State


class UserDaily(StatesGroup):
    list_topics = State()
    template = State()
    timezone = State()
    edit_topics = State()
    type_img = State()


class EthCC_Main_Event(StatesGroup):
    day = State()
    location = State()
    topic = State()

class FeedBack(StatesGroup):
    tg_id = State()
    text_feedback = State()
    username = State()

class FindList(StatesGroup):
    key = State()