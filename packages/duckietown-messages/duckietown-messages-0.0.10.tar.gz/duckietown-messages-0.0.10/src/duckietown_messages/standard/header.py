from typing import Optional

from pydantic import Field

from ..base import BaseMessage


class Header(BaseMessage):
    # version of the message this header is attached to
    version: str = Field(
        description="Version of the message this header is attached to",
        regex=r"^[0-9]+\.[0-9]+(\.[0-9]+)?$",
        example="0.1.3",
        default="1.0"
    )
    # reference frame this data is captured in
    frame: Optional[str] = Field(description="Reference frame this data is captured in", default=None)
    # auxiliary data for the message
    txt: Optional[dict] = Field(description="Auxiliary data attached to the message", default=None)


AUTO = Field(default_factory=Header, description="Auto-generated header")
