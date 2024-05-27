from __future__ import annotations

import asyncio
import io
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
  pass


async def resize_image_bytes(image_data: bytes, size: tuple[int,int] = (80,80)) -> bytes:
  loop = asyncio.get_running_loop()
  image = await loop.run_in_executor(None, lambda: Image.open(io.BytesIO(image_data)))
  image = await loop.run_in_executor(None, image.resize, size, Image.LANCZOS)
  output_bytes = io.BytesIO()
  await loop.run_in_executor(None, lambda: image.save(output_bytes, format="png"))
  output_bytes.seek(0)
  return output_bytes.read()

async def convert_to_png(image_data: bytes) -> bytes:
  loop = asyncio.get_running_loop()
  image = await loop.run_in_executor(None, lambda: Image.open(io.BytesIO(image_data)))
  output_bytes = io.BytesIO()
  await loop.run_in_executor(None, lambda: image.save(output_bytes, format="png"))
  output_bytes.seek(0)
  return output_bytes.read()