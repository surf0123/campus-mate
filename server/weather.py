import os
from datetime import datetime, timedelta

import httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
BASE_TIMES = ["2300", "2000", "1700", "1400", "1100", "0800", "0500", "0200"]


def _fetch_items(base_date: str, base_time: str) -> list[dict]:
    params = {
        "serviceKey": os.environ["KMA_API_KEY"],
        "numOfRows": "1000",
        "pageNo": "1",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": os.environ["NX"],
        "ny": os.environ["NY"],
    }
    resp = httpx.get(API_URL, params=params, timeout=10)
    resp.raise_for_status()
    body = resp.json().get("response", {}).get("body", {})
    return body.get("items", {}).get("item", [])


def get_weather_today() -> dict | None:
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    base_time = now.strftime("%H%M")

    # 발표 시각(02,05,08,...,23시) 중 현재 이전의 가장 최근 값으로 요청
    candidates = [t for t in BASE_TIMES if t <= base_time]
    if not candidates:
        now -= timedelta(days=1)
        base_date = now.strftime("%Y%m%d")
        candidates = BASE_TIMES

    items = []
    for base_time in candidates[:3]:
        items = _fetch_items(base_date, base_time)
        if items:
            break
    if not items:
        return None

    def first_value(category: str) -> str | None:
        for item in items:
            if item.get("category") == category:
                return item.get("fcstValue")
        return None

    sky_code = first_value("SKY")
    sky_map = {"1": "맑음", "3": "구름많음", "4": "흐림"}
    pop = first_value("POP")
    pty = first_value("PTY")

    try:
        pop_int = int(pop) if pop is not None else 0
    except ValueError:
        pop_int = 0
    raining = pty is not None and pty != "0"

    return {
        "temperature": float(first_value("T1H") or 0),
        "sky": sky_map.get(sky_code, "알 수 없음"),
        "precipitation_probability": pop_int,
        "umbrella": pop_int >= 50 or raining,
    }
