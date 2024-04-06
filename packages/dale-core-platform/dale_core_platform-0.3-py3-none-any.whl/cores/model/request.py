from pydantic import BaseModel
from typing import AnyStr, Optional


class RequestObjModel(BaseModel):
    def __str__(self) -> str:
        return 'RequestObjModel'
    
    token: Optional[str] = str()
    header: Optional[dict] = dict()
    method: Optional[str] = str()
    files: Optional[list] = list()
    body: Optional[dict|str] = dict()
    

class ResponseObjModel(RequestObjModel):
    def __str__(self) -> str:
        return 'ResponseObjModel'
    status_code: int = int()
    status_msg: str = str()
    errors: AnyStr = str()
    # grpc_code: int = int() # not applicable
    # api_version: float = float() # not applicable
    message: AnyStr = str()
    response_data: dict = dict()
    meta_data: dict = dict()
