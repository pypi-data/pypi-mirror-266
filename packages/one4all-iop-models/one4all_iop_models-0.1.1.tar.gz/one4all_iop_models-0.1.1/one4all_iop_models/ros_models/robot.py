from typing import List, Union

import pandas as pd
from pydantic import BaseModel, Field


class RobotPositionBase (BaseModel):
    PoseWithCovariance_PositionX: float
    PoseWithCovariance_PositionY: float
    PoseWithCovariance_PositionZ: float
    PoseWithCovariance_OrientationX: float
    PoseWithCovariance_OrientationY: float
    PoseWithCovariance_OrientationZ: float
    PoseWithCovariance_OrientationW: float
    Odom_Pose_PositionX: float
    Odom_Pose_PositionY: float
    Odom_Pose_PositionZ: float
    Odom_Pose_OrientationX: float
    Odom_Pose_OrientationY: float
    Odom_Pose_OrientationZ: float
    Odom_Pose_OrientationW: float
    Odom_Twist_LinearX: float
    Odom_Twist_LinearY: float
    Odom_Twist_LinearZ: float
    Odom_Twist_AngularX: float
    Odom_Twist_AngularY: float
    Odom_Twist_AngularZ: float
    Path_PositionX: List[float]
    Path_PositionY: List[float]
    Path_PositionZ: List[float]
    Path_OrientationX: List[float]
    Path_OrientationY: List[float]
    Path_OrientationZ: List[float]
    Path_OrientationW: List[float]

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
    x: float = Field(ge=-5, le=5)
    y: float = Field(ge=-5, le=5)
    angle: float = Field(ge=0, le=360)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "awcombo"


class Joint(RobotActionBase):
    j1: float = Field(ge=-1, le=1)
    j2: float = Field(ge=-1, le=1)
    j3: float = Field(ge=-1, le=1)
    j4: float = Field(ge=-1, le=1)
    j5: float = Field(ge=-1, le=1)
    j6: float = Field(ge=-1, le=1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "joint"


class Carte(RobotActionBase):
    x: float = Field(ge=-1, le=1)
    y: float = Field(ge=-1, le=1)
    z: float = Field(ge=-1, le=1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "carte"


class Increm(RobotActionBase):
    axis: str = Field(choices=["x", "y", "z"])
    delta: float

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "increm"


RobotActionsTypes = Union[Increm, AWCombo, Carte, Joint]


class SubTask(BaseModel):
    actions: List[RobotActionsTypes]