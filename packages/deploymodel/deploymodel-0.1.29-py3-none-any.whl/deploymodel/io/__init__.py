from pydantic import BaseModel as PydanticBaseModel, Field


class BaseModel(PydanticBaseModel):
    ...


class ModelInput(BaseModel):
    ...


class ModelOutput(BaseModel):
    ...


__all__ = [
    "PydanticBaseModel",
    "Field",
    "ModelInput",
    "ModelOutput",
]
