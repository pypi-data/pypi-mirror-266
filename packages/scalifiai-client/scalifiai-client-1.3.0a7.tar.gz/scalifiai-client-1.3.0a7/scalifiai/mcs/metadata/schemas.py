from pydantic import BaseModel, validator, Field, ValidationError
from typing import Union
from pathlib import Path

from .constants import DATA_TYPES_SIMPLE_LITERAL, DATA_TYPES_STORAGE_LITERAL


class CreateMetadataSimpleProperties(BaseModel):

    value: Union[str, int, float]

    @validator("value", pre=True)
    def ensure_correct_type(cls, value):
        if isinstance(value, int):
            return value
        elif isinstance(value, float):
            return value
        elif isinstance(value, str):
            return value
        raise ValueError("Must be either str, int, or float")


class CreateMetadataSimple(BaseModel):

    key: str
    data_type: DATA_TYPES_SIMPLE_LITERAL
    properties: CreateMetadataSimpleProperties = Field(validation_alias="value")


class CreateMetadataStorage(BaseModel):

    key: str
    data_type: DATA_TYPES_STORAGE_LITERAL
    file_path: Path

    @validator(
        "file_path", pre=True
    )  # pre=True to run this before the standard validators
    def check_file_path(cls, value):
        try:
            path = Path(value)
        except Exception as ex:
            raise ValueError(str(ex))
        if not path.exists():
            raise ValueError(f"The path `{value}` does not exist.")
        if not path.is_file():
            raise ValueError(f"The path `{value}` is not a valid file.")
        return path


class UpdateMetadataSimpleProperties(BaseModel):

    value: Union[str, int, float]

    @validator("value", pre=True)
    def ensure_correct_type(cls, value):
        if isinstance(value, int):
            return value
        elif isinstance(value, float):
            return value
        elif isinstance(value, str):
            return value
        raise ValueError("Must be either str, int, or float")
