from pydantic import BaseModel, Field
from enum import Enum


class Models(str, Enum):
    snr = 'snr'
    dcn = 'dcn'
    dlink = 'dlink'
    bdcom = 'bdcom'
    tplink = 'tplink'
    zyxel = 'zyxel'
    orion = 'orion'


class DefaultResponse(BaseModel):
    data: str | int | dict | None = None
    message: str | None = None
    success: bool
