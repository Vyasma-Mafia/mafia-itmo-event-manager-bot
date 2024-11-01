import json

import requests

from database.models import UserProfile
from database.requests import get_users_with_polemica_id
from utils import setup_logger

logger = setup_logger()


async def get_club_rating() -> str:
    resp = requests.get(
        "https://app.polemicagame.com/v1/clubs/289/metrics?startDate=2024-09-01T00:00:00.000&endDate=2025-08-31T23:59:59.999")
    if resp.status_code != 200:
        logger.warn(resp.text)
        return "Неизвестная ошибка"
    data = json.loads(resp.text)
    registered_users: list[UserProfile] = list(await get_users_with_polemica_id())
    ranking = []
    for user in data:
        db_users = list(filter(lambda it: it.polemica_id == user["id"], registered_users))
        if len(db_users) == 0:
            continue
        db_user: UserProfile = db_users[0]

        username = db_user.nickname
        # Суммируем totalScores и totalAwards из всех категорий
        total_score = sum(category["totalScores"] for category in user["metrics"].values())
        total_awards = sum(category["totalAwards"] for category in user["metrics"].values())

        # Добавляем пользователя в рейтинг
        ranking.append({"username": username, "totalScores": total_score, "totalAwards": total_awards})

    # Сортируем рейтинг по totalScores в порядке убывания
    ranking = sorted(ranking, key=lambda x: x["totalScores"], reverse=True)[:10]

    # Выводим топ-результат
    ranks_texts = []
    for rank, user in enumerate(ranking, 1):
        ranks_texts.append(f"<code>{rank}. {user['username'].ljust(15)} {user['totalScores']}</code>")
    return "\n".join(ranks_texts)
