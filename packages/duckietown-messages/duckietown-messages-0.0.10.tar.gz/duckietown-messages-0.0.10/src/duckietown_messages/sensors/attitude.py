from pydantic import Field
from ..base import BaseMessage
from ..standard.header import Header, AUTO


class Attitude(BaseMessage):
    # header
    header: Header = AUTO

    # angular acceleration about the 3 axis
    roll: float = Field(description="Roll angle in degrees", ge=-180, le=180)
    pitch: float = Field(description="Pitch angle in degrees", ge=-180, le=180)
    yaw: float = Field(description="Yaw angle in degrees", ge=-180, le=180)