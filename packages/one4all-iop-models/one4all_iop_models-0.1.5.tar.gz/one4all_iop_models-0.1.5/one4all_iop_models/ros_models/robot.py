from typing import List, Union, Literal

from pydantic import BaseModel, confloat, conlist, validator


class RobotPosition (BaseModel):
    amcl_positions: conlist(float, min_length=3, max_length=3)
    amcl_orientations: conlist(float, min_length=4, max_length=4)
    odom_pose_positions: conlist(float, min_length=3, max_length=3)
    odom_pose_orientations: conlist(float, min_length=4, max_length=4)
    odom_twist_linear: conlist(float, min_length=3, max_length=3)
    odom_twist_angular: conlist(float, min_length=3, max_length=3)
    path_positions: conlist(List[float], min_length=3, max_length=3)
    path_orientations: conlist(List[float], min_length=4, max_length=4)


class AWCombo(BaseModel):
    name: Literal["awcombo"] = "awcombo"
    x: float = confloat(ge=-5, le=5)
    y: float = confloat(ge=-5, le=5)
    angle: float = confloat(ge=0, le=360)

    @validator('name')
    def validate_name(cls, v):
        if v != "awcombo":
            raise ValueError("name must be 'awcombo'")
        return v

    def __init__(self, name, x, y, angle):
        self.x = x
        self.y = y
        self. angle = angle


class Joint(BaseModel):
    name: Literal["joint"] = "joint"
    j1: float = confloat(ge=-1, le=1)
    j2: float = confloat(ge=-1, le=1)
    j3: float = confloat(ge=-1, le=1)
    j4: float = confloat(ge=-1, le=1)
    j5: float = confloat(ge=-1, le=1)
    j6: float = confloat(ge=-1, le=1)

    @validator('name')
    def validate_name(cls, v):
        if v != "joint":
            raise ValueError("name must be 'joint'")
        return v

    def __init__(self, name, j1, j2, j3, j4, j5, j6):
        self.j1 = j1
        self.j2 = j2
        self.j3 = j3
        self.j4 = j4
        self.j5 = j5
        self.j6 = j6


class Carte(BaseModel):
    name: Literal["carte"] = "carte"
    x: float = confloat(ge=-1, le=1)
    y: float = confloat(ge=-1, le=1)
    z: float = confloat(ge=-1, le=1)

    @validator('name')
    def validate_name(cls, v):
        if v != "carte":
            raise ValueError("name must be 'carte'")
        return v

    def __init__(self, name, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Increm(BaseModel):
    name: Literal["increm"] = "increm"
    axis: Literal["x", "y", "z"]
    delta: float

    @validator('name')
    def validate_name(cls, v):
        if v != "increm":
            raise ValueError("name must be 'increm'")
        return v

    def __init__(self, name, axis, delta):
        self.axis = axis
        self.delta = delta


class SubTask(BaseModel):
    actions: List[Union[Increm, AWCombo, Carte, Joint]]
