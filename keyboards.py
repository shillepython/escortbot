import configparser

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


models_b = "💝 Модели"
profile_b = "👤 Профиль"
info_b = "ℹ️ Информация"
admin_b = "Админка"
worker_b = "Меню воркера"


def main_menu(isAdmin = False, user: list = False):
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    profile = KeyboardButton(text=profile_b)
    models = KeyboardButton(text=models_b)
    info = KeyboardButton(text=info_b)
    menu.add(models)
    menu.row(profile, info)
    if isAdmin is True:
        admin = KeyboardButton(text=admin_b)
        menu.add(admin)
    if user is not None and user[2] == 1:
        worker = KeyboardButton(text=worker_b)
        menu.add(worker)
    return menu


def admin_panel():
    menu = InlineKeyboardMarkup(row_width=2)
    delete_form = InlineKeyboardButton(text="Удалить анкету", callback_data="delete_form_admin")
    give_worker = InlineKeyboardButton(text="Выдать статус воркера", callback_data="give_worker")
    menu.row(delete_form, give_worker)
    return menu


def profile():
    menu = InlineKeyboardMarkup(row_width=1)
    my_orders = InlineKeyboardButton(text="🔍 Мои заказы", callback_data="my_orders_user")
    menu.add(my_orders)
    return menu


def worker_panel():
    menu = InlineKeyboardMarkup(row_width=1)
    statistic = InlineKeyboardButton(text="Статистика", callback_data="statistic_worker")
    add_model = InlineKeyboardButton(text="Добавить модель", callback_data="add_model_worker")
    my_models = InlineKeyboardButton(text="Мои модели", callback_data="my_models_worker")
    admin = InlineKeyboardButton(text="Помощь админа", callback_data="help_admin")
    menu.add(statistic)
    menu.row(add_model, my_models)
    menu.add(admin)
    return menu


def skip_button():
    skip = InlineKeyboardMarkup(row_width=1)
    skip.add(InlineKeyboardButton('Пропустить', callback_data='skip'))
    return skip

def finish_upload():
    finish_upload_button = InlineKeyboardMarkup(row_width=1)
    finish_upload_button.add(InlineKeyboardButton('Завершить загрузку', callback_data='finish_upload'))
    return finish_upload_button


def close_tab():
    menu = InlineKeyboardMarkup(row_width=1)
    my_orders = InlineKeyboardButton(text="Закрыть", callback_data="my_orders_user")
    menu.add(my_orders)
    return my_orders


def confirm_add_girl():
    menu = InlineKeyboardMarkup(row_width=1)
    yes = InlineKeyboardButton(text="Подтвердить", callback_data="confirm_add_girl_1")
    no = InlineKeyboardButton(text="Отменить", callback_data="confirm_add_girl_0")
    menu.row(yes, no)
    return menu


def inforamation_buttons():
    menu = InlineKeyboardMarkup(row_width=1)
    config = configparser.ConfigParser()
    config.read('addons/config.ini')
    feedbacks = InlineKeyboardButton(text="💬️ Отзывы", url=config['Bot']['feedback_channel'])
    support = InlineKeyboardButton(text="🆘 Поддержка", url=f"https://t.me/{config['Support']['support_username'].replace('@', '')}")
    guarante = InlineKeyboardButton(text="💯 Гарантии", url=config["Bot"]["garantii"])
    # menu.add(feedbacks)
    menu.row(support, guarante)
    return menu


# МОДЕЛИ
def show_all_models(index_page, data):
    count_all_models = len(data)

    menu = InlineKeyboardMarkup(row_width=1)
    count_in_page = 10
    last_page = False
    girls = []

    # Calculate start and end indices based on index_page
    start = (index_page - 1) * count_in_page
    end = start + count_in_page

    try:
        for girl in data[start:end]:
            girls.append(girl)
    except Exception as ex:
        print(ex)

    if len(girls) < 10:
        last_page = True

    for girl in girls:
        girl_b = InlineKeyboardButton(text=f"(#{girl[0]}) · {girl[1]} · {girl[2]}",
                                      callback_data=f"show_girl_number_{girl[0]}_{index_page}")
        menu.add(girl_b)

    # Add pagination buttons
    if count_all_models <= count_in_page:
        # Only one page of models, no pagination needed
        pass
    elif last_page is True:
        # Last page, add only previous page button
        page_b = InlineKeyboardButton(text="<<", callback_data=f"change_page_{index_page - 1}")
        menu.add(page_b)
    elif last_page is False and index_page == 1 and len(girls) == 10:
        # First page, add only next page button
        page_b = InlineKeyboardButton(text=">>", callback_data=f"change_page_{index_page + 1}")
        menu.add(page_b)
    elif last_page is False and index_page != 1:
        # Middle page, add both previous and next page buttons
        prev_b = InlineKeyboardButton(text="<<", callback_data=f"change_page_{index_page - 1}")
        page_b = InlineKeyboardButton(text=">>", callback_data=f"change_page_{index_page + 1}")
        menu.row(prev_b, page_b)
    else:
        # Error condition, add previous page button as fallback
        page_b = InlineKeyboardButton(text="<<", callback_data=f"change_page_{index_page - 1}")
        menu.add(page_b)
    close_ta = InlineKeyboardButton(text="❌ Закрыть", callback_data=f"close_tab")
    menu.add(close_ta)
    return menu


def model_keys(girl, index_page, photo_index=0):
    menu = InlineKeyboardMarkup(row_width=1)
    girl_num = girl[0]
    services = InlineKeyboardButton(text="Услуги", callback_data=f"girl_services_{girl_num}")
    next_photo = InlineKeyboardButton(text="Следующее фото",
                                      callback_data=f"girl_next_photo_{girl_num}_{index_page}_{photo_index}")
    prev_photo = InlineKeyboardButton(text="Предыдущее фото",
                                      callback_data=f"girl_prev_photo_{girl_num}_{index_page}_{photo_index}")
    nudes_photos = InlineKeyboardButton(text="Обнаженные фото",
                                        callback_data=f"girl_nudes_photos_{girl_num}_{index_page}")
    buy = InlineKeyboardButton(text="Оформить", callback_data=f"girl_buy_{girl_num}_{index_page}")
    back = InlineKeyboardButton(text="⏪ Назад", callback_data=f"girl_back_{index_page}")

    # Добавляем кнопки, если это не первое или не последнее фото
    if photo_index > 0:
        menu.add(prev_photo)
    if photo_index < len(girl[6].split(";")) - 1:
        menu.add(next_photo)

    menu.add(services)
    menu.add(nudes_photos)
    menu.add(buy)
    menu.add(back)

    return menu


def buy_girl(girl, index_page):
    menu = InlineKeyboardMarkup(row_width=1)
    price_per_hour = int(girl[3])
    price_per_2_hour = int(float(price_per_hour) * 1.8)
    price_per_night = int(float(price_per_2_hour) * 1.8)
    buy_per_1 = InlineKeyboardButton(text=f"🌇 Час - {price_per_hour}₽", callback_data=f"buy_per_{price_per_hour}_{girl[0]}_{index_page}")
    buy_per_2 = InlineKeyboardButton(text=f"🏙 2 часа - {price_per_2_hour}₽", callback_data=f"buy_per_{price_per_2_hour}_{girl[0]}_{index_page}")
    buy_per_24 = InlineKeyboardButton(text=f"🌃 Ночь - {price_per_night}₽", callback_data=f"buy_per_{price_per_night}_{girl[0]}_{index_page}")
    back = InlineKeyboardButton(text="⏪ Назад", callback_data=f"show_girl_number_{girl[0]}_{index_page}")
    menu.add(buy_per_1)
    menu.add(buy_per_2)
    menu.add(buy_per_24)
    menu.add(back)
    return menu


def choose_payment(girl, index_page, price):
    menu = InlineKeyboardMarkup(row_width=1)
    card = InlineKeyboardButton(text=f"💳 Карта", callback_data=f"choose_payment_{girl[0]}_{index_page}_{price}_card")
    tex = InlineKeyboardButton(text=f"👨‍💻 Пополнить через поддержку", callback_data=f"choose_payment_{girl[0]}_{index_page}_{price}_tex")
    usdt = InlineKeyboardButton(text=f"💷 USD-T (TRC-20)", callback_data=f"choose_payment_{girl[0]}_{index_page}_{price}_usdt")
    eth = InlineKeyboardButton(text=f"💷 ETH", callback_data=f"choose_payment_{girl[0]}_{index_page}_{price}_eth")
    btc = InlineKeyboardButton(text=f"💷 BTC", callback_data=f"choose_payment_{girl[0]}_{index_page}_{price}_btc")
    back = InlineKeyboardButton(text="⏪ Назад", callback_data=f"show_girl_number_{girl[0]}_{index_page}")
    menu.add(card)
    menu.add(tex)
    menu.add(usdt)
    menu.add(eth)
    menu.add(btc)
    menu.add(back)
    return menu


def check_payment(girl, index_page):
    menu = InlineKeyboardMarkup(row_width=1)
    yes = InlineKeyboardButton(text=f"⭕️ Проверить оплату", callback_data=f"check_payment_{girl[0]}_{index_page}")
    no = InlineKeyboardButton(text=f"❌ Отменить", callback_data=f"show_girl_number_{girl[0]}_{index_page}")
    menu.add(yes)
    menu.add(no)
    return menu


def back_page(girl, index_page):
    menu = InlineKeyboardMarkup(row_width=1)
    no = InlineKeyboardButton(text=f"❌ Отменить", callback_data=f"show_girl_number_{girl[0]}_{index_page}")
    menu.add(no)
    return menu