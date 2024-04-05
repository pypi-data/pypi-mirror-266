# Assuming these models exist in xoa_container/models/config.py or similar

from typing import List, Optional

from pydantic import BaseModel


class HypervisorConfig(BaseModel):
    host: str
    username: str
    password: str
    autoConnect: Optional[bool] = True
    allowUnauthorized: Optional[bool] = False


# class XOAInstance(BaseModel):
#     host: str
#     rest_api: Optional[str] = None
#     websocket: Optional[str] = None
#     username: str
#     password: str


class UserConfig(BaseModel):
    username: str
    password: str
    permission: Optional[str] = "none"


class ApplyConfig(BaseModel):
    # xoa: XOAInstance
    hypervisors: List[HypervisorConfig]
    users: List[UserConfig]
