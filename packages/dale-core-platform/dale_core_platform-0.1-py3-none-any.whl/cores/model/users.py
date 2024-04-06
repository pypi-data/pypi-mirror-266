from pydantic import BaseModel


class UserObjModel(BaseModel):
    user_name: str = str()
    user_pwd: str = str()
    user_first_name: str = str()
    user_last_name: str = str()
    user_age: int = int()
    user_profession: str = str()
    user_type: str = str()


class PermissionObj(BaseModel):
    pass


class RoleObj(BaseModel):
    pass
