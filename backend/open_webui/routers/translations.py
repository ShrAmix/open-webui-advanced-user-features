import logging
import os
from typing import Optional

import aiohttp
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from open_webui.models.users import Users
from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.internal.db import get_session
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)
router = APIRouter()

KNESS_APP_API_BASE_URL = os.environ.get(
    "KNESS_APP_API_BASE_URL",
    "http://dev-test.kness.team/kness-app-api"
)
OPEN_WEB_UI_API_BASE_URL = os.environ.get(
    "OPEN_WEB_UI_API_BASE_URL",
    "http://dev-test.kness.team/open_web_ui_api"
)


class TierUpdateRequest(BaseModel):
    email: str
    tier: str


############################
# Admin: Отримати підписки всіх користувачів
############################


@router.get("/admin/subscriptions")
async def get_admin_subscriptions(
    user=Depends(get_admin_user),
    db: Session = Depends(get_session),
):
    # Отримуємо всіх користувачів open-webui
    result = Users.get_users(filter={}, skip=0, limit=1000, db=db)
    all_users = result["users"]
    users_by_email = {u.email: u for u in all_users}

    # Один запит до kness-app-api за всіма підписками
    kness_subscriptions = {}
    try:
        async with aiohttp.ClientSession(trust_env=True) as session:
            url = f"{KNESS_APP_API_BASE_URL}/api/v1/client/subscriptions/all"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15), ssl=False) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    items = response.get("data", response) if isinstance(response, dict) else response
                    for item in items:
                        kness_subscriptions[item["email"]] = item["subscription"]
    except Exception as e:
        log.warning(f"Не вдалося отримати підписки з kness-app-api: {e}")

    # Мержимо: показуємо тільки юзерів open-webui, додаємо підписку з kness-app-api
    results = []
    for u in all_users:
        results.append({
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "role": u.role,
            "profile_image_url": u.profile_image_url,
            "subscription": kness_subscriptions.get(u.email, None),
        })

    return results


############################
# Admin: Змінити тарифний план підписки
############################


@router.put("/admin/subscription")
async def update_admin_subscription(
    form_data: TierUpdateRequest,
    user=Depends(get_admin_user),
):
    valid_tiers = ["standard", "plus", "pro"]
    if form_data.tier not in valid_tiers:
        raise HTTPException(status_code=400, detail=f"Невірний тариф. Допустимі: {', '.join(valid_tiers)}")

    try:
        async with aiohttp.ClientSession(trust_env=True) as session:
            url = f"{KNESS_APP_API_BASE_URL}/api/v1/client/subscription/{form_data.email}/tier"
            async with session.post(
                url,
                json={"tier": form_data.tier},
                timeout=aiohttp.ClientTimeout(total=10),
                ssl=False,
            ) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    return response.get("data", response) if isinstance(response, dict) and "data" in response else response
                else:
                    text = await resp.text()
                    raise HTTPException(status_code=resp.status, detail=text)
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=502, detail=f"Не вдалося оновити підписку: {str(e)}")


############################
# User: Get my subscription
############################


@router.get("/subscription")
async def get_my_subscription(
    user=Depends(get_verified_user),
):
    try:
        async with aiohttp.ClientSession(trust_env=True) as session:
            url = f"{KNESS_APP_API_BASE_URL}/api/v1/client/subscription/{user.email}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10), ssl=False) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    return response.get("data", response) if isinstance(response, dict) and "data" in response else response
                else:
                    return {"documentTranslation": None}
    except Exception as e:
        log.warning(f"Failed to fetch subscription for {user.email}: {e}")
        return {"documentTranslation": None}


############################
# User: Get my translation history
############################


@router.get("/history")
async def get_my_translation_history(
    limit: int = 50,
    offset: int = 0,
    user=Depends(get_verified_user),
):
    try:
        async with aiohttp.ClientSession(trust_env=True) as session:
            url = f"{OPEN_WEB_UI_API_BASE_URL}/deepl/cache/history"
            params = {
                "limit": limit,
                "offset": offset,
                "email": user.email,
            }
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10), ssl=False) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"success": False, "count": 0, "total": 0, "history": []}
    except Exception as e:
        log.warning(f"Failed to fetch translation history for {user.email}: {e}")
        return {"success": False, "count": 0, "total": 0, "history": []}
