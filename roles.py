from pydantic import BaseModel
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    parent = "parent"
    coach = "coach"
    viewer = "viewer"





