from typing import List, Union, Literal

import pandas as pd
from pydantic import BaseModel, confloat, conlist, validator


class RobotPositionBase (BaseModel):
    amcl_positions: conlist(float, min_length=3, max_length=3)
    amcl_orientations: conlist(float, min_length=4, max_length=4)
    odom_pose_positions: conlist(float, min_length=3, max_length=3)
    odom_pose_orientations: conlist(float, min_length=4, max_length=4)
    odom_twist_linear: conlist(float, min_length=3, max_length=3)
    odom_twist_angular: conlist(float, min_length=3, max_length=3)
    path_positions: conlist(List[float], min_length=3, max_length=3)
    path_orientations: conlist(List[float], min_length=4, max_length=4)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame):
        parsed_data = df.to_dict(orient='records')
        models = []
        for row in parsed_data:
            model = cls(**row)
            models.append(model)
        return models


class RobotActionBase(BaseModel):
    name: str


class AWCombo(RobotActionBase):
    name: str = "awcombo"
    x: float = confloat(ge=-5, le=5)
    y: float = confloat(ge=-5, le=5)
    angle: float = confloat(ge=0, le=360)

    @validator('name')
    def validate_name(cls, v):
        if v != "awcombo":
            raise ValueError("name must be 'awcombo'")
        return v

    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self. angle = angle


class Joint(RobotActionBase):
    name: str = "joint"
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

    def __init__(self, j1, j2, j3, j4, j5, j6):
        self.j1 = j1
        self.j2 = j2
        self.j3 = j3
        self.j4 = j4
        self.j5 = j5
        self.j6 = j6


class Carte(RobotActionBase):
    name: str = "carte"
    x: float = confloat(ge=-1, le=1)
    y: float = confloat(ge=-1, le=1)
    z: float = confloat(ge=-1, le=1)

    @validator('name')
    def validate_name(cls, v):
        if v != "joint":
            raise ValueError("name must be 'carte'")
        return v

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Increm(RobotActionBase):
    name: str = "increm"
    axis: Literal["x", "y", "z"]
    delta: float

    @validator('name')
    def validate_name(cls, v):
        if v != "joint":
            raise ValueError("name must be 'increm'")
        return v

    def __init__(self, axis, delta):
        self.axis = axis
        self.delta = delta


class SubTask(BaseModel):
    actions: List[Union[Increm, AWCombo, Carte, Joint]]
