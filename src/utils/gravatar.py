from __future__ import annotations

import hashlib
from enum import Enum
from typing import TYPE_CHECKING

import yarl

if TYPE_CHECKING:
  from aiohttp import ClientSession

class Defaults(Enum):
  DEFAULT = "mp"
  MYSTERY = "mp"
  IDENTICON = "identicon"
  MONSTERID = "monsterid"
  WAVATAR = "wavatar"
  RETRO = "retro"
  ROBOHASH = "robohash"
  BLANK = "blank"

class Rating(Enum):
  G = "g",
  PG = "pg",
  R = "r"
  X = "x"

def hash(data: str) -> str:
  "Create a hash for gravatar"
  return hashlib.sha256(data.strip().lower().encode()).hexdigest()

async def gravatar(
    data: str,
    *,
    url: str = "https://gravatar.com/avatar/",
    size: int = 80,
    default: Defaults = Defaults.RETRO,
    force_default: bool = False,
    rating: Rating = Rating.G,
    extension: str = "png",
    download: bool = False,
    cs: ClientSession = None
  ) -> str|bytes:
  # First, build the URL.
  query = {
    "size": size,
    "d": default.value,
    "forcedefault": "y" if force_default else "n",
    "rating": rating.value
  }

  url = yarl.URL.build(
    scheme="https",
    host="gravatar.com",
    path=f"/avatar/{data}.{extension}",
    query=query
  )

  if not download:
    return str(url)
  if cs is None:
    raise ValueError("Must pass download=true and cs!")
  
  async with cs.get(url) as resp:
    data = await resp.read()
    return data