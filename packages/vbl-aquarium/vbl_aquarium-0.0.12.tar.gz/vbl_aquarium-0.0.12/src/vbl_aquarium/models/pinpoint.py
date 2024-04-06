from __future__ import annotations

from vbl_aquarium.models.unity import Vector2, Vector3
from vbl_aquarium.utils.vbl_base_model import VBLBaseModel

# CRANIOTOMY


class CraniotomyModel(VBLBaseModel):
    index: int
    size: Vector2
    position: Vector3
    rectangle: bool = False


class CraniotomyGroup(VBLBaseModel):
    atlas: str
    data: list[CraniotomyModel]
