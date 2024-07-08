from aiogram.dispatcher.filters.state import State, StatesGroup


class Register(StatesGroup):
    city = State()
    ref_code = State()


class AdminDeleteForm(StatesGroup):
    form_id = State()


class AdminAddWorker(StatesGroup):
    worker_id = State()


class AddModelWorker(StatesGroup):
    about = State()
    confirm = State()