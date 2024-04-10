from pydantic import Field
from ..base import BaseMessage
from ..standard.header import Header, AUTO

## TODO: Fully define the BatteryState message to be compatible with the ROS message definition 
##      http://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/BatteryState.html
 
class BatteryState(BaseMessage):
    header: Header = AUTO

    voltage: float = Field(description="Voltage of the battery", ge=0)
    present: bool = Field(description="True if the battery is present, False otherwise")


