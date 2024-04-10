from pydantic import Field

from ..base import BaseMessage
from ..standard.header import Header, AUTO


class AngularVelocities(BaseMessage):
    # header
    header: Header = AUTO

    # angular acceleration about the 3 axis
    x: float = Field(description="Angular acceleration about the x axis")
    y: float = Field(description="Angular acceleration about the y axis")
    z: float = Field(description="Angular acceleration about the z axis")
