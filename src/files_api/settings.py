from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """Settings for the files API.

    Pydantic BaseSettings docs: https://docs.pydantic.dev/latest/concepts/pydantic_settings/#usage
    FastAPI guide to managing settings: https://fastapi.tiangolo.com/advanced/settings/
    """

    # as far as python is concerned,
    # this class has a default value with it being set to Field(...).
    # When pydantic tries to read vals from the env the 3 dots will
    # indicate this is a required field so pydantic will raise a
    # validation error if thats the case
    s3_bucket_name: str = Field(...)

    model_config = SettingsConfigDict(case_sensitive=False)
