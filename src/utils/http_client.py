import httpx
from src.utils.logging import logger

async def async_http_post(url: str, data: dict, headers: dict = None):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            return response
        except httpx.TimeoutException:
            logger.error(f"Timeout while calling {url}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Error calling {url}: {str(e)}")
            raise