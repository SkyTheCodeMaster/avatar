from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import web
from aiohttp.web import Response
from utils.authenticate import authenticate, get_project_status
from utils import gravatar, avatar

if TYPE_CHECKING:
  from utils.extra_request import Request

routes = web.RouteTableDef()


def validate_parameters(body: dict, params: list[str]) -> tuple[bool, str]:
  for param in params:
    if param not in body:
      return False, param
  return True, ""


@routes.post("/user/set/")
async def post_user_set(request: Request) -> Response:
  user = await authenticate(request)

  if isinstance(user, Response):
    return user

  status = await get_project_status(user, "avatar", cs=request.session)

  if status is False:
    return Response(
      status=401,
      body="please apply for avatar project at https://auth.skystuff.cc/projects#avatar",
    )

  body = await request.json()
  ok, missing = validate_parameters(body, ["type"])

  if not ok:
    return Response(status=400, body=f"missing {missing} in body")

  avatar_type = avatar.AvatarType(body["type"])

  if avatar_type == avatar.AvatarType.URL:
    if "url" not in body:
      return Response(
        status=400, body=f"must pass url if type is {avatar_type.value}"
      )

    await request.conn.execute(
      """INSERT INTO
          Users (Name, Email, AvatarType, AvatarURL)
        VALUES
          ($1,$2,$3,$4)
        ON CONFLICT (Name)
          DO UPDATE SET
            AvatarType = $3
            AvatarURL = $4;""",
      user.username,
      gravatar.hash(user.email),
      avatar_type.value,
      body["url"],
    )
  else:
    await request.conn.execute("""INSERT INTO
          Users (Name, Email, AvatarType)
        VALUES
          ($1,$2,$3)
        ON CONFLICT (Name)
          DO UPDATE SET
            AvatarType = $3;""",
          user.username,
          gravatar.hash(user.email),
          avatar_type.value)
  return Response()


async def setup(app: web.Application) -> None:
  for route in routes:
    app.LOG.info(f"  ↳ {route}")
  app.add_routes(routes)
