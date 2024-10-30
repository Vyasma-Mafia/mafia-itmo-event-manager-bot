import json
from dataclasses import dataclass
from typing import List, Optional

import requests

from config import ACHIEVEMENT_SERVICE_HOST


@dataclass
class Achievement:
    description: str
    name: str
    id: str
    order: int
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


def get_level_emoji(level: int) -> str:
    level_emojis = {
        0: "➖",
        1: "⭐",
        2: "🌟",
        3: "💫",
        4: "🚀",
        5: "🏆"
    }
    return level_emojis.get(level, "")


def get_user_achievement(achievement: Achievement, level: int = 0, progress: int = 0) -> str:
    return f"""
{get_level_emoji(level)} <u>{level}</u> <b>{achievement.name}</b> {get_my_level(achievement, level, progress)} 
    <i>{achievement.description}</i>
"""


def get_my_level(achievement: Achievement, level: Optional[int], progress: int):
    if level is None:
        level = 0
    next_level_score = "∞" if (level == len(achievement.levels)) else achievement.levels[level]
    return f"({progress} / {next_level_score})"


def levelsString(achievement: Achievement):
    levels = []
    for i in range(len(achievement.levels)):
        levels.append((achievement.levels[i], i + 1))
    return "/".join(map(lambda it: f"{it[0]} {get_level_emoji(it[1])}", levels))


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
            get_user_achievement(achievement, achievement_gain.achievementLevel, achievement_gain.achievementCounter))
    for achievement in achievements_map.values():
        achievements_messages.append(
            get_user_achievement(achievement))
    return "".join(achievements_messages)
