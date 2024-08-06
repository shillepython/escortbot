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
    confirm_about = State()
    photos = State()
    confirm_photos = State()
    nude_photos = State()
    confirm = State()
