from pydantic import BaseModel
from typing import Optional


class EnvObjModel(BaseModel):
    env: Optional[str] = str()
    base_url: Optional[str]
    base_api_url: Optional[str]
    browser: Optional[str] = str()
    is_api: bool = bool()
    is_web: bool = bool()
    is_ios: bool = bool()
    is_android: bool = bool()
    is_mobile: bool = bool()
    is_e2e: bool = bool()
    project_name: str = str()
    log_level: str = str()
    is_headless: bool = bool()
    is_testlink: bool = bool()
    swagger_url: Optional[str] = str()
    token: Optional[str] = str()
    platform_id: Optional[int] = int()
