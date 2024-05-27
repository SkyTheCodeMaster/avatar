from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import web
from aiohttp.web import Response
from utils import avatar, gravatar

if TYPE_CHECKING:
  from utils.extra_request import Request

routes = web.RouteTableDef()


@routes.get("/avatar/{username:.*}")
async def get_avatar(request: Request) -> Response:
  username = request.match_info.get("username", None)
  query = request.query
  if username is None:
    return Response(status=404)

  try:
    _size = int(query.get("size", 80))
    _size = max(1, min(2000, _size))
    size = (_size, _size)
  except ValueError:
    return Response(status=400, text="size parameter must be integer!")

  data = await avatar.get_avatar(
    username, cs=request.session, conn=request.conn, size=size
  )

  if data is False:
    if request.app.config["avatar"]["show_default_if_user_doesnt_exist"]:
      hashed = gravatar.hash(username)
      data = await gravatar.gravatar(
        hashed,
        default=gravatar.Defaults[
          request.app.config["avatar"]["default_mode"].upper()
        ],
        force_default=True,
        download=True,
        cs=request.session,
        size=size[0],
      )
      return Response(body=data, content_type="image/png")
    else:
      return Response(status=404)

  return Response(body=data, content_type="image/png")


@routes.get("/preview/{data:.*}")
async def get_preview(request: Request) -> Response:
  data = request.match_info.get("data", None)
  query = request.query
  if data is None:
    return Response(status=404)

  try:
    _size = int(query.get("size", 80))
    _size = max(1, min(2000, _size))
    size = (_size, _size)
  except ValueError:
    return Response(status=400, text="size parameter must be integer!")

  try:
    avatar_type = gravatar.Defaults[query.get("style", "retro").upper()]
  except Exception:
    return Response(
      status=400,
      body=f"invalid type, valid: {','.join([e.name for e in gravatar.Defaults])}",
    )

  avatar_data = await gravatar.gravatar(
    data,
    size=size[0],
    default=avatar_type,
    force_default=True,
    download=True,
    cs=request.session,
  )
  return Response(body=avatar_data, content_type="image/png")


@routes.get("/img/{username:.*}")
async def get_img(request: Request) -> Response:
  username = request.match_info.get("username", None)
  if username is None:
    return Response(status=404)

  data = await avatar.get_internal_avatar(username, request.conn)

  if data is False:
    return Response(status=404)

  return Response(body=data, content_type="image/png")


async def setup(app: web.Application) -> None:
  for route in routes:
    app.LOG.info(f"  ↳ {route}")
  app.add_routes(routes)
