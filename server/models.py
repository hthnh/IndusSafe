from pydantic import BaseModel
from datetime import datetime

class MotorData(BaseModel):
    U1: float
    U2: float
    U3: float
    I1: float
    I2: float
    I3: float
    timestamp: datetime
