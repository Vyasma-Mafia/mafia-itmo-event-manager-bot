import json
from asyncio import timeout
from types import SimpleNamespace as Namespace
from dataclasses import dataclass
from typing import Optional
import jsonpickle

import requests

from config import ACHIEVEMENT_SERVICE_HOST
from plugins.achievements import PolemicaUser
from utils import setup_logger

logger = setup_logger()


@dataclass
class PairStat:
    firstUser: Optional[PolemicaUser]
    secondUser: Optional[PolemicaUser]
    firstRedSecondRedWin: int
    firstRedSecondRedTotal: int
    firstRedSecondBlackWin: int
    firstRedSecondBlackTotal: int
    firstBlackSecondRedWin: int
    firstBlackSecondRedTotal: int
    firstBlackSecondBlackWin: int
    firstBlackSecondBlackTotal: int


def deserialize_pair_stat(json_data: str) -> PairStat:
    data = jsonpickle.decode(json_data)
    data["firstUser"] = None if "firstUser" not in data else PolemicaUser(**data["firstUser"])
    data["secondUser"] = None if "secondUser" not in data else PolemicaUser(**data["secondUser"])
    ans = PairStat(**data)
    return ans


def get_pair_stat_text(first_polemica_id: int, second_polemica_id: int) -> str:
    response = requests.get(f"{ACHIEVEMENT_SERVICE_HOST}/research/pairStat",
                            params={"firstId": first_polemica_id, "secondId": second_polemica_id},
                            timeout=30)
    if response.status_code != 200:
        logger.warn(response.text)
        return "Произошла неизвестная ошибка"
    ans: PairStat = deserialize_pair_stat(response.text)
    logger.info(f"Pair rating for {userText(ans.firstUser)}, {userText(ans.secondUser)}")
    return f"""
Игрок 1: {userText(ans.firstUser)}, Игрок 2: {userText(ans.secondUser)}
<b>Вместе красные</b>: {winrateText(ans.firstRedSecondRedWin, ans.firstRedSecondRedTotal)}
<b>Вместе черные</b>: {winrateText(ans.firstBlackSecondBlackWin, ans.firstBlackSecondBlackTotal, True)}
<b>Красный 1 vs черный 2</b>: {winrateText(ans.firstRedSecondBlackWin, ans.firstRedSecondBlackTotal)}
<b>Черный 1 vs красный 2</b>: {winrateText(ans.firstBlackSecondRedWin, ans.firstBlackSecondRedTotal, True)}
"""


def userText(user: Optional[PolemicaUser]):
    if user is None:
        return f"Неизвестный"
    else:
        return f"<b>{user.username}</b>({user.id})"


def winrateText(win: int, total: int, invert: bool = False):
    real_win = win if not invert else total - win
    return f"побед <b>{real_win}</b>, всего <b>{total}</b>, винрейт {0 if total == 0 else int(real_win / total * 100)}%"
