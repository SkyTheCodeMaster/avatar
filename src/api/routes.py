from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING

from aiohttp import web
from aiohttp.web import Response

from utils.authenticate import authenticate, get_project_status
from utils.cors import add_cors_routes

if TYPE_CHECKING:
  from utils.extra_request import Request

with open("config.toml") as f:
  config = tomllib.loads(f.read())
  frontend_version = config["pages"]["frontend_version"]
  api_version = config["srv"]["api_version"]

routes = web.RouteTableDef()

@routes.get("/srv/get/")
async def get_lp_get(request: Request) -> Response:
  packet = {
    "frontend_version": frontend_version,
    "api_version": api_version,
  }

  if request.app.POSTGRES_ENABLED:
    database_size_record = await request.conn.fetchrow("SELECT pg_size_pretty ( pg_database_size ( current_database() ) );")
    packet["db_size"] = database_size_record.get("pg_size_pretty","-1 kB")

  return web.json_response(packet)

@routes.get("/srv/authtest/")
async def get_srv_authtest(request: Request) -> Response:
  user = await authenticate(request)
  if isinstance(user, Response):
    return user
  
  approval = await get_project_status(user, "avatar", cs=request.session)

  if not approval:
    return Response(status=401,body="please apply for avatar project at https://auth.skystuff.cc/projects#avatar")
  
  return Response(text=f"you are {user.username}, and you are {approval.name} for avatar project.")

async def setup(app: web.Application) -> None:
  for route in routes:
    app.LOG.info(f"  ↳ {route}")
  app.add_routes(routes)
  add_cors_routes(routes, app)