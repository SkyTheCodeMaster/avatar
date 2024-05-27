from __future__ import annotations

import tomllib
from enum import Enum
from typing import TYPE_CHECKING

from utils import gravatar, image

if TYPE_CHECKING:
  from aiohttp import ClientSession
  from asyncpg import Connection

# Take in username, resolve avatar.
with open("config.toml") as f:
  config = tomllib.loads(f.read())

class AvatarType(Enum):
  DEFAULT = 0
  URL = 1
  GRAVATAR = 2
  RETRO = 3
  IDENTICON = 4
  MONSTERID = 5
  WAVATAR = 6
  ROBOHASH = 7


async def get_internal_avatar(username: str, conn: Connection) -> bytes | False:
  "Fetches avatar from Avatars table."

  record = await conn.fetchrow(
    "SELECT * FROM Avatars WHERE Username = $1;", username
  )

  if record is None:
    return False

  return record["data"]


async def get_avatar(
  username: str, *, cs: ClientSession, conn: Connection, size: tuple[int,int] = (80,80)
) -> bytes:
  "Take a username, return avatar bytes"
  user_record = await conn.fetchrow(
    "SELECT * FROM Users WHERE Name=$1;", username
  )

  if not user_record:
    return False

  avatar_type = AvatarType(user_record["avatartype"])

  match avatar_type:
    case AvatarType.DEFAULT:
      avatar_bytes = await gravatar.gravatar(
        "",
        default=gravatar.Defaults.MYSTERY,
        force_default=True,
        download=True,
        cs=cs,
        size=size[0]
      )
    case AvatarType.URL:
      # More advanced logic to check if an entry exists in the internal image table to save time.
      url: str = user_record["avatarurl"]
      if url.startswith(f"{config['srv']['public_url']}/img/"):
        avatar_bytes = await get_internal_avatar(user_record["username"])
      else:
        async with cs.get(url) as resp:
          avatar_bytes = await resp.read()
      
    case AvatarType.GRAVATAR:
      avatar_bytes = await gravatar.gravatar(
        user_record["email"],
        download=True,
        cs=cs,
        size=size[0]
      )
    case AvatarType.RETRO:
      avatar_bytes = await gravatar.gravatar(
        user_record["email"],
        default=gravatar.Defaults.RETRO,
        force_default=True,
        download=True,
        cs=cs,
        size=size[0]
      )
    case AvatarType.IDENTICON:
      avatar_bytes = await gravatar.gravatar(
        user_record["email"],
        default=gravatar.Defaults.IDENTICON,
        force_default=True,
        download=True,
        cs=cs,
        size=size[0]
      )
    case AvatarType.MONSTERID:
      avatar_bytes = await gravatar.gravatar(
        user_record["email"],
        default=gravatar.Defaults.MONSTERID,
        force_default=True,
        download=True,
        cs=cs,
        size=size[0]
      )
    case AvatarType.WAVATAR:
      avatar_bytes = await gravatar.gravatar(
        user_record["email"],
        default=gravatar.Defaults.WAVATAR,
        force_default=True,
        download=True,
        cs=cs,
        size=size[0]
      )
    case AvatarType.ROBOHASH:
      avatar_bytes = await gravatar.gravatar(
        user_record["email"],
        default=gravatar.Defaults.ROBOHASH,
        force_default=True,
        download=True,
        cs=cs,
        size=size[0]
      )

  # By the end of this, avatar_bytes should be a png.
  png_bytes = await image.convert_to_png(avatar_bytes)
  resized = await image.resize_image_bytes(png_bytes, size)

  return resized