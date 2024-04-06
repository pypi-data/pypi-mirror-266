from pydantic import BaseModel
# from typing import Optional


class DbConnModel(BaseModel):
    db_type: str = str()
    db_name: str = str()
    db_username: str = str()
    db_pwd: str = str()
    db_host: str = str()
    db_port: int = int()
