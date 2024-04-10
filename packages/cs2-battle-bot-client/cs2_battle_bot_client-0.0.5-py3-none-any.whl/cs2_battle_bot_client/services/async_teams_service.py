import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


async def teams_list(page: Optional[int] = None, api_config_override: Optional[APIConfig] = None) -> PaginatedTeamList:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/teams/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"page": page}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return PaginatedTeamList(**response.json()) if response.json() is not None else PaginatedTeamList()


async def teams_create(data: Team, api_config_override: Optional[APIConfig] = None) -> Team:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/teams/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request("post", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 201:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Team(**response.json()) if response.json() is not None else Team()


async def teams_retrieve(id: str, api_config_override: Optional[APIConfig] = None) -> Team:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/teams/{id}/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Team(**response.json()) if response.json() is not None else Team()


async def teams_update(id: str, data: Team, api_config_override: Optional[APIConfig] = None) -> Team:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/teams/{id}/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request("put", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Team(**response.json()) if response.json() is not None else Team()


async def teams_destroy(id: str, api_config_override: Optional[APIConfig] = None) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/teams/{id}/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 204:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return None


async def teams_partial_update(id: str, data: PatchedTeam, api_config_override: Optional[APIConfig] = None) -> Team:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/teams/{id}/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            "patch", httpx.URL(path), headers=headers, params=query_params, json=data.dict()
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Team(**response.json()) if response.json() is not None else Team()
