import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class ERPAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    async def login(self, username: str, password: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"username": username, "password": password},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("access_token") or data.get("token")
            except httpx.HTTPError as e:
                logger.error("Login failed: %s", e)
                return None

    async def get_products(self, token: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/products",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict) and "items" in data:
                    return data["items"]
                if isinstance(data, list):
                    return data
                return []
            except httpx.HTTPError as e:
                logger.error("Failed to fetch products: %s", e)
                return []

    async def get_customers(self, token: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/customers",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict) and "items" in data:
                    return data["items"]
                if isinstance(data, list):
                    return data
                return []
            except httpx.HTTPError as e:
                logger.error("Failed to fetch customers: %s", e)
                return []

    async def get_customer_debts(
        self, token: str, customer_id: Optional[int] = None
    ) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/api/v1/accounting/customers/debts"
                if customer_id:
                    url = f"{url}?customer_id={customer_id}"
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict) and "items" in data:
                    return data["items"]
                if isinstance(data, list):
                    return data
                return []
            except httpx.HTTPError as e:
                logger.error("Failed to fetch customer debts: %s", e)
                return []

    async def create_customer_debt(
        self, token: str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/accounting/customers/debts",
                    json=data,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error("Failed to create customer debt: %s", e)
                return None

    async def get_suppliers(self, token: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/suppliers",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict) and "items" in data:
                    return data["items"]
                if isinstance(data, list):
                    return data
                return []
            except httpx.HTTPError as e:
                logger.error("Failed to fetch suppliers: %s", e)
                return []

    async def get_dashboard(self, token: str) -> Optional[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/dashboard",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error("Failed to fetch dashboard: %s", e)
                return None
