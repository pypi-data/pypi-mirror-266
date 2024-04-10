from pydantic import Field

from ..base import BaseMessage
from ..colors.rgba import RGBA
from ..standard.header import Header, AUTO


class CarLights(BaseMessage):
    # header
    header: Header = AUTO

    # lights
    front_left: RGBA = Field(description="Front left light color and intensity")
    front_right: RGBA = Field(description="Front right light color and intensity")
    rear_left: RGBA = Field(description="Rear left light color and intensity")
    rear_right: RGBA = Field(description="Rear right light color and intensity")
