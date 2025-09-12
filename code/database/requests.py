from datetime import datetime
from logging import exception
from typing import Optional

from sqlalchemy import and_
from sqlalchemy import select, delete, update, func

from config import ADMIN_CHAT_ID
from database.models import Admin, BannedUser, UserInMailing, Event, EventSingUp, UserProfile
from database.models import async_session
from utils import setup_logger

logger = setup_logger()


async def get_events():
    async with async_session() as session:
        return await session.scalars(select(Event))


async def get_unremoved_events():
    async with async_session() as session:
        return await session.scalars(select(Event).where(Event.removed == False))


async def add_in_mailing(*, chat_id: int):
    async with async_session() as session:
        # Проверяем находиться-ли пользователь в рассылке
        user = await session.scalar(select(UserInMailing).where(UserInMailing.chat_id == chat_id))
        # Если пользователя нет в таблице, то добавляем его
        if not user:
            session.add(UserInMailing(chat_id=chat_id))
            await session.commit()


async def check_is_signup_open(*, event_name: str):
    async with async_session() as session:
        return await session.scalar(select(Event).where((Event.is_signup_open == 1) &
                                                        (Event.name == event_name)))


async def close_signup_to_event(*, event_name: str):
    async with async_session() as session:
        await session.execute(update(Event).where(Event.name == event_name).
                              values(is_signup_open=0))
        await session.commit()


async def del_from_mailing(*, chat_id: int):
    async with async_session() as session:
        await session.execute(delete(UserInMailing).where(UserInMailing.chat_id == chat_id))
        await session.commit()


async def add_in_ban(*, chat_id: int):
    async with async_session() as session:
        session.add(BannedUser(chat_id=chat_id))
        await session.commit()


async def del_from_ban(*, chat_id: int):
    async with async_session() as session:
        await session.execute(delete(BannedUser).where(BannedUser.chat_id == chat_id))
        await session.commit()


async def add_in_admin(*, chat_id: int):
    async with async_session() as session:
        session.add(Admin(chat_id=chat_id))
        await session.commit()


async def del_from_admin(*, chat_id: int):
    async with async_session() as session:
        await session.execute(delete(Admin).where(Admin.chat_id == chat_id))
        await session.commit()


async def get_users_from_mailing():
    async with async_session() as session:
        return await session.scalars(select(UserInMailing))


async def get_chat_ids_for_users_in_mailing(event_id: int) -> list[int]:
    async with async_session() as session:
        # Define the query
        query = (select(UserInMailing.chat_id)
                 .join(EventSingUp, UserInMailing.chat_id == EventSingUp.chat_id)
                 .where(EventSingUp.event_id == int(event_id))
                 .where(EventSingUp.event_status == 1))

        # Execute and fetch the results
        try:
            result = await session.execute(query)
        except exception as e:
            print(e)

        chat_ids = result.scalars().all()

        return chat_ids


async def check_ban(*, chat_id: int):
    async with async_session() as session:
        return await session.scalar(select(BannedUser).where(BannedUser.chat_id == chat_id))


async def check_admin(*, chat_id: int):
    async with async_session() as session:
        if str(chat_id) == ADMIN_CHAT_ID:
            return True
        else:
            return await session.scalar(select(Admin).where(Admin.chat_id == chat_id))


async def add_event_to_table(*, event_name: str, event_description: str,
                             event_date: datetime, is_signup_open: int = 1,
                             event_limit: int = 40, removed: bool = False):
    async with async_session() as session:
        session.add(Event(name=event_name, description=event_description,
                          date=event_date,  # Make sure this is a datetime object
                          limit=event_limit,
                          is_signup_open=is_signup_open,
                          removed=removed))
        await session.commit()


async def delete_event_from_table(*, event_id: int):
    async with async_session() as session:
        await session.execute(delete(Event).where(Event.id == event_id))
        await session.commit()
        await session.execute((delete(EventSingUp).where(EventSingUp.event_id == event_id)))
        await session.commit()


async def remove_event_from_table(*, event_id: int):
    async with async_session() as session:
        await session.execute(update(Event).where(Event.id == event_id).values(removed=True))
        await session.commit()


async def check_event_by_name(*, event_name: str):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.name == event_name))


async def check_event_by_id(*, event_id: int):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.id == event_id))


async def get_event_name_by_id(*, event_id: int):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.id == event_id))


async def get_event_info_by_name(*, event_name: str):
    async with async_session() as session:
        return await session.scalar(select(Event).where(Event.name == event_name))


async def add_signup_user(*, event_name: str, full_name: str, chat_id: int, level: str, username: str):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        existing_signup = await session.scalar(
            select(EventSingUp).where(
                and_(
                    EventSingUp.event_id == id_of_event,
                    EventSingUp.chat_id == chat_id
                )
            )
        )
        if existing_signup:
            if existing_signup.event_status != 1:
                # Удаляем существующую запись
                await session.delete(existing_signup)
                # Создаём новую запись
                session.add(EventSingUp(
                    chat_id=chat_id,
                    full_name=full_name,
                    event_id=id_of_event,
                    level=level,
                    username=username,
                    event_status=1
                ))
        else:
            # Создаём новую запись
            session.add(EventSingUp(
                chat_id=chat_id,
                full_name=full_name,
                event_id=id_of_event,
                level=level,
                username=username,
                event_status=1
            ))
        await session.commit()


async def check_signup(*, event_name: str, chat_id: int):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        return await session.scalar(
            select(EventSingUp).where(
                and_(
                    EventSingUp.event_id == id_of_event,
                    EventSingUp.chat_id == chat_id,
                    EventSingUp.event_status == 1  # Проверяем только активные записи
                )
            )
        )


async def check_go_to_event(*, event_name: str, chat_id: int):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        return await session.scalar(select(EventSingUp).where((EventSingUp.event_status == 1) &
                                                              (EventSingUp.event_id == id_of_event) &
                                                              (EventSingUp.chat_id == chat_id)))


async def get_full_info_about_singup_user(*, event_name: str, chat_id: int):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        return await session.scalar(select(EventSingUp).where((EventSingUp.event_id == id_of_event) &
                                                              (EventSingUp.chat_id == chat_id)))


async def change_signup_status(*, event_name: str, chat_id: int):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        await session.execute(update(EventSingUp).where((EventSingUp.event_id == id_of_event) &
                                                        (EventSingUp.chat_id == chat_id)).
                              values(event_status=0))
        await session.commit()


async def get_count_of_signup(*, event_name: str):
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        return await session.scalar(select(func.count(EventSingUp.id)).filter((EventSingUp.event_status == 1) &
                                                                              (EventSingUp.event_id == id_of_event)))


async def get_count_of_events():
    async with async_session() as session:
        return await session.scalar(select(func.count(Event.id)))


async def get_signup_people(*, event_name: str):
    async with async_session() as session:
        session.expire_all()
        session.expunge_all()
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        people: dict = {
            "Полное имя": [],
            # "Телефон": [],
            "Айди чата": [],
            "Уровень": [],
            "Никнейм": [],
            "вуз": []
        }
        signup_people = await session.scalars(
            select(EventSingUp)
            .where((EventSingUp.event_status == 1) &
                   (EventSingUp.event_id == id_of_event))
            .order_by(EventSingUp.id)
        )
        for user in signup_people:
            user_profile_data = await get_user_profile(chat_id=user.chat_id)
            people["Полное имя"] += [user.full_name]
            # people["Телефон"] += [user.phone]
            people["вуз"] += ["ИТМО" if user_profile_data.is_itmo else "Гость"]
            people["Айди чата"] += [user.chat_id]
            people["Уровень"] += [user.level]
            people["Никнейм"] += [user.username]
            # Добавляем уровень
            # telegram_user = await bot.get_chat(user.chat_id)
            # people["Никнейм"].append(telegram_user.username)
        return people


# Сохранение и получение профиля
async def save_user_profile(chat_id: int,
                            nickname: str,
                            is_itmo: bool,
                            level: int,
                            polemica_id: Optional[int],
                            full_name: Optional[str] = None,
                            passport: Optional[str] = None,
                            phone: Optional[str] = None,
                            username: Optional[str] = None,
                            personal_data_agreement: bool = False):
    async with async_session() as session:
        profile = await session.scalar(select(UserProfile).where(UserProfile.chat_id == chat_id))
        if profile:
            profile.nickname = nickname
            profile.level = level
            profile.is_itmo = is_itmo
            profile.polemica_id = polemica_id
            profile.full_name = full_name
            profile.passport = passport
            profile.phone = phone
            profile.username = username
            profile.personal_data_agreement = personal_data_agreement
        else:
            session.add(UserProfile(chat_id=chat_id,
                                    nickname=nickname,
                                    is_itmo=is_itmo,
                                    level=level,
                                    polemica_id=polemica_id,
                                    full_name=full_name,
                                    passport=passport,
                                    phone=phone,
                                    username=username,
                                    personal_data_agreement=personal_data_agreement
                                    ))
        await session.commit()


async def get_user_profile(chat_id: int) -> Optional[UserProfile]:
    async with async_session() as session:
        return await session.scalar(select(UserProfile).where(UserProfile.chat_id == chat_id))


async def get_users_with_polemica_id() -> list[UserProfile]:
    async with async_session() as session:
        return await session.scalars(select(UserProfile).where(UserProfile.polemica_id != None))


async def get_guest_count_for_event(event_name: str) -> int:
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        return await session.scalar(
            select(func.count(EventSingUp.id)).join(UserProfile, EventSingUp.chat_id == UserProfile.chat_id).where(
                (EventSingUp.event_status == 1) &
                (EventSingUp.event_id == id_of_event) &
                (UserProfile.is_itmo == False)
            )
        )

async def get_guests_for_event(event_name: str) -> list[UserProfile]:
    async with async_session() as session:
        id_of_event = (await session.scalar(select(Event).where(Event.name == event_name))).id
        result = await session.scalars(
            select(UserProfile).join(EventSingUp, UserProfile.chat_id == EventSingUp.chat_id).where(
                (EventSingUp.event_status == 1) &
                (EventSingUp.event_id == id_of_event) &
                (UserProfile.is_itmo == False)
            )
        )
        return result.all()
