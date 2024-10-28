import json
from dataclasses import dataclass
from typing import List

import requests

from config import ACHIEVEMENT_SERVICE_HOST


@dataclass
class Achievement:
    description: str
    name: str
    id: str
    levels: List[int]


@dataclass
class PolemicaUser:
    id: int
    username: str


@dataclass
class AchievementGainAnswer:
    user: PolemicaUser
    achievementId: str
    achievementLevel: int
    achievementCounter: int


@dataclass
class AchievementsWithGains:
    achievements: List[Achievement]
    achievementsGains: List[AchievementGainAnswer]


def deserialize_achievements_with_gains(json_data: str) -> AchievementsWithGains:
    data = json.loads(json_data)
    achievements = [
        Achievement(**ach) for ach in data['achievements']
    ]
    if 'achievementsGains' in data:
        achievements_gains = [
            AchievementGainAnswer(
                user=PolemicaUser(**ag['user']),
                achievementId=ag['achievementId'],
                achievementLevel=ag['achievementLevel'],
                achievementCounter=ag['achievementCounter']
            ) for ag in data['achievementsGains']
        ]
    else:
        achievements_gains = []
    return AchievementsWithGains(achievements=achievements, achievementsGains=achievements_gains)


def get_user_achievement(achievement: Achievement, achievement_gain: AchievementGainAnswer):
    return f"""
<b>{achievement.name}</b> Уровень {achievement_gain.achievementLevel}
    <i>{achievement.description}</i>
    Уровни: {levelsString(achievement)}
    Прогресс: {achievement_gain.achievementCounter}
"""


def levelsString(achievement):
    return " / ".join(map(str, achievement.levels))


def get_achievement(achievement: Achievement):
    return f"""
<b>{achievement.name}</b>
    <i>{achievement.description}</i>
    Уровни: {levelsString(achievement)}
"""


def get_user_achievements_text(polemica_id: int) -> str:
    response = requests.get(f"http://{ACHIEVEMENT_SERVICE_HOST}/achievements", params={"ids": polemica_id})
    if response.status_code != 200:
        return "Произошла неизвестная ошибка"
    ans = deserialize_achievements_with_gains(response.text)
    achievements_map: dict[str, Achievement] = {}
    for achievement in ans.achievements:
        achievements_map[achievement.id] = achievement

    achievements_messages = []
    for achievement_gain in ans.achievementsGains:
        achievement = achievements_map[achievement_gain.achievementId]
        achievements_map.pop(achievement.id)
        achievements_messages.append(
            get_user_achievement(achievement, achievement_gain))
    for achievement in achievements_map.values():
        achievements_messages.append(
            get_achievement(achievement))
    return "\n".join(achievements_messages)
