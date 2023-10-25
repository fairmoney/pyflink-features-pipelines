from typing import Optional

from pydantic import BaseModel, Field


class BaseSourceConfig(BaseModel):
    source_name: str = Field(
        description="The name of the source",
        default=...
    )
    transformation_function_arg_name: str = Field(
        default=...,
        description="Argument name used to pass the loaded DataStream to the transformation function"
    )

