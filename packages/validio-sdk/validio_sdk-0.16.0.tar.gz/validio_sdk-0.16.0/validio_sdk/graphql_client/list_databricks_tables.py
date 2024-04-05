from typing import List

from pydantic import Field

from .base_model import BaseModel


class ListDatabricksTables(BaseModel):
    databricks_list_tables: List[str] = Field(alias="databricksListTables")


ListDatabricksTables.model_rebuild()
