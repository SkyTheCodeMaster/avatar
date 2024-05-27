# Handle authentication and request verification
from __future__ import annotations

import json
from enum import Enum
from typing import TYPE_CHECKING

from aiohttp.web import Response

if TYPE_CHECKING:
  from aiohttp import ClientSession

  from .extra_request import Application, Request


class Approval(Enum):
  DEFAULT = 0
  APPROVED = 1
  PENDING = 2
  DENIED = 3


class User:
  username: str
  super_admin: bool
  email: str
  token: str

  def __init__(
    self, *, username: str, super_admin: bool, email: str, token: str
  ) -> None:
    self.username = username
    self.super_admin = super_admin
    self.email = email
    self.token = token


# All this does is authenticate a user existing.
async def authenticate(
  request: Request, *, cs: ClientSession = None
) -> User | Response:
  app: Application = request.app
  if cs is None:
    cs = app.cs

  # We prioritize header authentication over cookie authentication.
  auth_token = request.cookies.get("Authorization", None)
  auth_token = request.headers.get("Authorization", auth_token)

  if auth_token is None:
    return Response(
      status=401, body="pass Authorization header or Authorization cookie."
    )

  auth_token = auth_token.removeprefix("Bearer ")

  # Now we want to send the request
  # Removing and adding Bearer is mildly redundant
  headers = {"Authorization": f"Bearer {auth_token}"}

  async with cs.get(
    "https://auth.skystuff.cc/api/user/get/", headers=headers
  ) as resp:
    if resp.status == 200:
      data = json.loads(await resp.text())
      u = User(
        username=data["name"],
        super_admin=data["super_admin"],
        email=data["email"],
        token=data["token"],
      )
      return u
    else:
      return Response(status=401, body="invalid token")


async def get_project_status(
  user: User, project_name: str, *, cs: ClientSession
) -> Approval | False:
  headers = {"Authorization": f"Bearer {user.token}"}
  async with cs.get(
    f"https://auth.skystuff.cc/api/project/status/{project_name}",
    headers=headers,
  ) as resp:
    if resp.status != 200:
      return False
    data = await resp.json()
    approval = Approval[data["approval"].upper()]
    return approval