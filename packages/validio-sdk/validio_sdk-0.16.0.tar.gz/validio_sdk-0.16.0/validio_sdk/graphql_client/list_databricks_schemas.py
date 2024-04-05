from typing import List

from pydantic import Field

from .base_model import BaseModel


class ListDatabricksSchemas(BaseModel):
    databricks_list_schemas: List[str] = Field(alias="databricksListSchemas")


ListDatabricksSchemas.model_rebuild()
