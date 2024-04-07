from pydantic import BaseModel, validator
from typing import List


class ModelVersionTag(BaseModel):

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


class CreateModelVersionTags(BaseModel):

    tags: List[ModelVersionTag]


class GenerateMetadataDownloadURL(BaseModel):

    metadata_id: int


class GenerateMetadataPreviewURL(GenerateMetadataDownloadURL):

    metadata_id: int
