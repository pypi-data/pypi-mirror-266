from pydantic import BaseModel, Field, validator
from typing import Optional, List


class CreateModel(BaseModel):

    verbose_name: str = Field(validation_alias="name")
    description: str
    sub_task: Optional[str]
    language: Optional[str]


class DeleteVersion(BaseModel):

    version: int


class ModelTag(BaseModel):

    key: str
    value: str

    @validator("value", pre=True)
    def convert_value(cls, v):

        converted_value = v

        try:
            converted_value = str(converted_value)
        except Exception:
            pass

        return converted_value


class CreateModelTags(BaseModel):

    tags: List[ModelTag]


class GenerateMetadataDownloadURL(BaseModel):

    metadata_id: int


class GenerateMetadataPreviewURL(GenerateMetadataDownloadURL):

    metadata_id: int
