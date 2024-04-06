from __future__ import annotations

from enum import Enum

from pydantic import Field

from vbl_aquarium.models.unity import Color, Vector2, Vector3
from vbl_aquarium.utils.vbl_base_model import VBLBaseModel

# CustomAtlas


class CustomAtlasModel(VBLBaseModel):
    name: str
    dimensions: Vector3
    resolution: Vector3


# CustomMesh


class CustomMeshData(VBLBaseModel):
    id: str = Field(alias="ID")
    vertices: list[Vector3]
    triangles: list[int]
    normals: list[Vector3] = None


class CustomMeshModel(VBLBaseModel):
    id: str = Field(alias="ID")
    position: Vector3
    use_reference: bool
    material: str
    scale: Vector3
    color: Color


# Area


class AtlasModel(VBLBaseModel):
    name: str
    reference_coord: Vector3 = None
    areas: list[StructureModel]
    colormap: ColormapModel


class StructureModel(VBLBaseModel):
    name: str
    acronym: str
    atlas_id: int
    color: Color
    # values that come with defaults:
    visible: bool = False
    color_intensity: float = -1
    side: int = 0
    material: str = "default"


# Camera


class CameraModel(VBLBaseModel):
    class CameraMode(str, Enum):
        orthographic = "orthographic"
        perspective = "perspective"

    id: str = Field(alias="ID")
    position: Vector3 = None
    rotation: Vector3 = Vector3()
    target: Vector3 = None
    zoom: float = 16
    pan: Vector2 = Vector2()
    mode: CameraMode = CameraMode.orthographic
    background_color: Color = Color() # white by default
    controllable: bool = True
    main: bool = False

class CameraRotationModel(VBLBaseModel):
    start_rotation: Vector3
    end_rotation: Vector3

# Individual mesh neuron


class PrimitiveMeshModel(VBLBaseModel):
    data: list[MeshModel]


class MeshModel(VBLBaseModel):
    id: str = Field(alias="ID")
    shape: str
    position: Vector3
    color: Color
    scale: Vector3
    material: str
    interactive: bool

# Lines
    
class LineModel(VBLBaseModel):
    id: str = Field(alias="ID")
    positions: list[Vector3] = []
    color: Color = Color()

# Probes
    
class ProbeModel(VBLBaseModel):
    id: str = Field(alias="ID")
    position: Vector3
    color: Color
    angles: Vector3
    style: str
    scale: Vector3

# Particle group


class ParticleSystemModel(VBLBaseModel):
    id: str = Field(alias="ID")
    n: int
    material: str = 'circle'

    positions: list[Vector3] = []
    sizes: list[float] = []
    colors: list[Color] = []

# Text
    
class TextModel(VBLBaseModel):
    id: str = Field(alias="ID")
    text: str
    color: Color = Color(r = 0, g = 0, b = 0)
    font_size: int = 12
    position: Vector2 = Vector2()

# Utilities
    
class ColormapModel(VBLBaseModel):
    name: str = ''
    min: float = 0
    max: float = 1