from typing import Union

from ...base import BaseMessage
from ...standard.header import Header, AUTO


class HILConnectionConfiguration(BaseMessage):
    # header
    header: Header = AUTO

    # connection configuration
    engine_url: Union[str, None]
    agent_name: Union[str, None]
    agent_configuration: Union[str, None]
    dreamwalking: bool = False
