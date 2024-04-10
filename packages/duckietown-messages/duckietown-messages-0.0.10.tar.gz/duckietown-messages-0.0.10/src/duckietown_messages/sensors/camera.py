from typing import Optional

from pydantic import Field

from ..base import BaseMessage
from ..standard.header import Header, AUTO


class Camera(BaseMessage):
    # header
    header: Header = AUTO

    width: int = Field(description="Width of the image", ge=0)
    height: int = Field(description="Height of the image", ge=0)
    K: list = Field(description="Intrinsic camera matrix")
    D: list = Field(description="Distortion coefficients")
    P: list = Field(description="Projection matrix")
    R: Optional[list] = Field(description="Rectification matrix", default=None)

    # TODO: this should not be here, a camera can have multiple homographies
    H: Optional[list] = Field(description="Homography matrix", default=None)
