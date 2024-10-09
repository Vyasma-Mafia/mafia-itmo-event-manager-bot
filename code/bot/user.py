import bot.keyboards as kb

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.requests import (check_ban, check_event_by_name, add_in_mailing, get_event_info_by_name, check_signup,
                               check_go_to_event, get_full_info_about_singup_user, change_signup_status, add_signup_user,
                               get_count_of_events, check_is_signup_open, get_signup_people)
from re import compile, search

# Чтобы не писать dispatcher 2-й раз заменим его на роутер
user = Router()

# Создаём класс (фильтр) для того, чтобы проверить забанен-ли пользователь


class BannedProtect(Filter):
    async def __call__(self, message: Message):
        return await check_ban(chat_id=message.from_user.id)

# Создаём класс (фильтр) для проверки является-ли сообщение названием мероприятия


class EventCheck(Filter):
    async def __call__(self, message: Message):
        return await check_event_by_name(event_name=message.text)

# Создаём класс (состояние) для записи на мероприятие


class EventSignUp(StatesGroup):
    event_name = State()
    full_name = State()
    id = State()
    level = State()
    username = State()
    confirm = State()

# Обработаем команду айди


@user.message(Command("id"))
async def id_command(message: Message):
    await message.answer(f"Ваш айди: {message.from_user.id}")

# Обработка сообщений от забаненного пользователя


@user.message(BannedProtect())
async def show_message_to_ban_user(message: Message):
    await message.answer("Вы забанены за плохое поведение!")


@user.message(CommandStart())
async def start_command(message: Message):
    await add_in_mailing(chat_id=message.from_user.id)
    sticker_id = "CAACAgIAAxkBAAEuSs5nBl1rNuFirPiPXjRVrUDOwTuMBgAClCEAApog6Ep3hdlbdFG1aTYE"
    await message.answer_sticker(sticker_id)
    await message.answer(f"Добро пожаловать, {message.from_user.first_name}!", reply_markup=await kb.get_start_menu(rights="user"))


@user.message(F.text == "🚫Отмена")
async def btn_cancel_click(message: Message, state: FSMContext):
    await state.set_state(EventSignUp.event_name)
    await message.answer("Отменяю действие", reply_markup=await kb.get_event_menu(rights="user", event_status="unsigned"))


@user.message(F.text == "👤Наши контакты")
async def btn_contacts_click(message: Message):
    await message.answer("Наши контакты:", reply_markup=kb.our_contacts)


@user.message(F.text == "💻Тех поддержка")
async def btn_support_click(message: Message):
    await message.answer("Техническая поддержка:", reply_markup=kb.tech_support)


@user.message(F.text == "🎉Мероприятия")
async def btn_events_click(message: Message):
    # Проверяем количество существующих мероприятий
    if await get_count_of_events() == 0:
        await message.answer("Нет мероприятий на которые можно записаться!")
    else:
        await message.answer("Выберите интересующее вас мероприятие!",
                             reply_markup=await kb.get_events_names_buttons())


@user.message(F.text == "👈Назад")
async def btn_back_click(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Открываю меню", reply_markup=await kb.get_start_menu(rights="user"))

# Обработка нажатий кнопок с названием мероприятий


@user.message(F.text == "🔄Обновить список")
async def refresh_registered_users(message: Message, state: FSMContext):
    data = await state.get_data()
    event_name = data.get('event_name')
    if event_name:
        await btn_event_name_click(message, state, event_name)
    else:
        await message.answer("Извините, не удалось обновить список. Пожалуйста, выберите мероприятие заново.")


@user.message(EventCheck())
async def btn_event_name_click(message: Message, state: FSMContext, event_name: str = None):
    event_info_for_message = '''🎉Название мероприятия: {event_name}
📆Дата и время проведения: <b>{event_date}</b>
🎊Описание: {event_desc}
👤Ограничение: <b>{event_limit} игроков</b>
✏️Запись: <b>{is_signup_open_str}</b>\n'''

    user_data_str = '''
📁Ваши данные :
👤Ник: {signup_user_full_name}\n
'''

    registered_users_str = "\nСписок зарегистрированных пользователей:\n{registered_users_list}\n"

    if event_name is None:
        event_name = message.text
        await state.set_state(EventSignUp.event_name)
        await state.update_data(event_name=event_name)
        await message.answer_sticker("CAACAgIAAxkBAAEDpPBl1WcOfjU0kJaSf9y882BG36ONiwACMw4AApVxCUiC2Rae9Yv1wzQE")

    await state.set_state(EventSignUp.event_name)
    chat_id = message.from_user.id
    event_info = await get_event_info_by_name(event_name=event_name)
    event_date = event_info.date
    event_desc = event_info.description
    event_limit = event_info.limit
    is_signup_open = await check_is_signup_open(event_name=event_name)
    is_signup_open_str = "открыта" if is_signup_open is not None else "закрыта"
    event_status = 'unsigned' if is_signup_open is not None else ''

    # Get the list of registered users
    registered_users = await get_signup_people(event_name=event_name)

    # Create a string with the list of registered users
    registered_users_list = ""
    print(registered_users)
    nicks = registered_users['Полное имя']
    tgs = registered_users['Никнейм']
    levels = registered_users['Уровень']
    is_signup_open_str = "открыта" if len(nicks) < event_limit else "закрыта"

    for i, (nick, level_id, username) in enumerate(zip(nicks, levels, tgs), start=1):
        print(user)

        level_symbol = next(
            (level['level_symbol'] for level in kb.LEVEL_DESCR if level['level_id'] == level_id), '')

        registered_users_list += f"{i}. {nick} {level_symbol} - @{username}\n"

    registered_users_str = registered_users_str.format(
        registered_users_list=registered_users_list)

    signup = await check_signup(event_name=event_name, chat_id=chat_id)
    if signup is None:
        # Пользователь не записан или запись отменена
        await message.answer(
            event_info_for_message.format(
                event_name=event_name,
                event_date=event_date,
                event_desc=event_desc,
                is_signup_open_str=is_signup_open_str,
                event_limit=event_limit
            ) + registered_users_str,
            parse_mode="HTML",
            reply_markup=await kb.get_event_menu(rights="user", event_status="unsigned", event_name=event_name)
        )
    else:
        full_info_about_signup_user = await get_full_info_about_singup_user(event_name=event_name, chat_id=chat_id)
        signup_user_full_name = full_info_about_signup_user.full_name

        if await check_go_to_event(event_name=event_name, chat_id=chat_id) is not None:
            await message.answer(
                event_info_for_message.format(event_name=event_name, event_date=event_date, event_desc=event_desc, is_signup_open_str=is_signup_open_str, event_limit=event_limit) +
                "🛎Статус : пойду\n" +
                registered_users_str,
                parse_mode="HTML",
                reply_markup=await kb.get_event_menu(rights="user", event_status="signed", event_name=event_name)
            )
        else:
            await message.answer(
                event_info_for_message.format(event_name=event_name, event_date=event_date, event_desc=event_desc, is_signup_open_str=is_signup_open_str, event_limit=event_limit) +
                user_data_str.format(signup_user_full_name=signup_user_full_name) +
                f"\n🛎Статус : не пойду"
                f"\n\n{registered_users_str}",
                parse_mode="HTML",
                reply_markup=await kb.get_event_menu(rights="user", event_name=event_name)
            )


@ user.message(F.text == "❌Я не приду", EventSignUp.event_name)
async def btn_dont_go_to_the_event_click(message: Message, state: FSMContext):
    data_from_state: dict = await state.get_data()
    event_name: str = data_from_state.get("event_name")
    chat_id = message.from_user.id
    if await check_signup(event_name=event_name, chat_id=chat_id) is None:
        await message.answer("Для начала запишитесь на мероприятие!")
    else:
        if await check_go_to_event(event_name=event_name, chat_id=chat_id) is not None:
            await state.update_data(id=chat_id)
            await message.answer("Вы точно не пойдёте на мероприятие?",
                                 #  "\nПримечание: после подтверждения вы больше не сможете"
                                 #  " записаться на это мероприятие!",
                                 reply_markup=await kb.get_confirm_menu("cofirm_dont_go_to_event"))
        else:
            await message.answer("Вы уже отменили запись!")

# Обработаем нажатие кнопок для отмены записи на мероприятие


@ user.callback_query(EventSignUp.event_name)
async def confirm_signup_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if callback.data == "cofirm_dont_go_to_event":
        data_from_state: dict = await state.get_data()
        event_name: str = data_from_state.get("event_name")
        chat_id: str = data_from_state.get("id")
        # Предполагается, что эта функция обновляет статус до 0 (отменено)
        await change_signup_status(event_name=event_name, chat_id=chat_id)
        await callback.message.answer("Вы успешно отменили запись!", reply_markup=await kb.get_events_names_buttons())
        await state.clear()
    else:
        await callback.message.answer("Отменяю действие!", reply_markup=await kb.get_event_menu(rights="user", event_status="signed"))

# Обработаем кнопку выхода из мероприятия


@ user.message(F.text == "🔙Назад")
async def btn_exit_from_events_click(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Перехожу назад", reply_markup=await kb.get_events_names_buttons())


@ user.message(F.text == "📝Записаться", EventSignUp.event_name)
async def btn_signup_click(message: Message, state: FSMContext):
    data_from_state: dict = await state.get_data()
    event_name: str = data_from_state.get("event_name")
    # Проверка открыта-ли запись
    if await check_is_signup_open(event_name=event_name) is not None:
        # Проверка записи на мерпориятие
        if await check_signup(event_name=event_name, chat_id=message.from_user.id) is None:
            signuped_users = await get_signup_people(event_name=event_name)
            current_signups = len(signuped_users["Полное имя"])
            event_info = await get_event_info_by_name(event_name=event_name)
            if current_signups < event_info.limit:
                await message.answer("Введите свой игровой ник\nПример : Фиалка",
                                     reply_markup=await kb.get_user_cancel_button())
                await state.set_state(EventSignUp.full_name)
            else:
                await message.answer("К сожалению, достигнут лимит участников для этого мероприятия.")
        else:
            await message.answer("Вы уже записались на это мерпориятие!")
    else:
        await message.answer("Запись на мероприятие уже закрыта!")


@ user.message(EventSignUp.full_name)
async def wait_full_name(message: Message, state: FSMContext):
    if message.text is not None:
        await state.update_data(full_name=message.text)
        await message.answer(
            'Выберите свой уровень. Описание уровней есть в <a href="https://t.me/mafia_itmo/64">посте</a>',
            reply_markup=await kb.get_level_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(EventSignUp.level)
    else:
        await message.answer("Некорректный ник! Попробуйте ещё раз!")


@ user.callback_query(EventSignUp.level)
async def level_selection_callback(callback: CallbackQuery, state: FSMContext):
    # Получаем выбранный уровень
    level_id = int(callback.data.split("_")[1])
    selected_level = next(
        (lvl for lvl in kb.LEVEL_DESCR if lvl["level_id"] == level_id), None)

    if selected_level:
        await state.update_data(level=selected_level)
        await state.update_data(id=callback.from_user.id)
        data_from_state: dict = await state.get_data()
        event_name: str = data_from_state.get("event_name")
        username = callback.from_user.username if callback.from_user.username else "No username"
        await state.update_data(username=username)
        full_name: str = data_from_state.get("full_name")
        user_level_dict: dict = data_from_state.get("level")
        await callback.message.answer(f"Подтвердите запись на мероприятие!"
                             f"\n🎉Название мероприятия : {event_name}"
                             f"\n📒Ваши данные : "
                             f"\n👤Игровой ник : {full_name}"
                             f"\n👤Уровень : {user_level_dict['level_symbol']}"
                             f"\n👤Ваш Telegram ник : @{username}",
                             reply_markup=await kb.get_confirm_menu("confirm_signup"))
        await state.set_state(EventSignUp.confirm)
    else:
        await callback.message.answer("Ошибка выбора уровня. Попробуйте снова.")


# Обработаем кнопку для подтверждения/отмены удаления мероприятия
@ user.callback_query(EventSignUp.confirm)
async def confirm_signup_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if callback.data == "confirm_signup":
        data_from_state: dict = await state.get_data()
        event_name: str = data_from_state.get("event_name")
        user_full_name: str = data_from_state.get("full_name")
        username: str = data_from_state.get("username")

        user_chat_id: str = data_from_state.get("id")
        user_level: dict = data_from_state.get("level")  # Уровень

        # Сохраняем запись вместе с уровнем
        await add_signup_user(
            event_name=event_name,
            full_name=user_full_name,
            chat_id=user_chat_id,
            username=username,
            level=user_level['level_id']  # Передаем уровень
        )
        await callback.message.answer("Вы успешно записались!", reply_markup=await kb.get_events_names_buttons())
        await state.clear()
    else:
        await callback.message.answer("Отменяю запись!\nВведите ник снова.", reply_markup=await kb.get_user_cancel_button())
        await state.set_state(EventSignUp.full_name)
