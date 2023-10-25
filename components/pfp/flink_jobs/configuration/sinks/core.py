from typing import Optional

from pydantic import BaseModel, Field


class BaseSinkConfig(BaseModel):
    sink_name: str = Field(
        description="The name of the source",
        default=...
    )
    sink_description: Optional[str] = Field(
        description="An optional description of the sink - to be displayed in Flink UI",
        default=None
    )
