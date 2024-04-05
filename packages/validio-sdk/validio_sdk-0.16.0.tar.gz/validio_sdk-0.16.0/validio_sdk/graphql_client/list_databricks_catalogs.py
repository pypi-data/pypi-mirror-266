from typing import List

from pydantic import Field

from .base_model import BaseModel


class ListDatabricksCatalogs(BaseModel):
    databricks_list_catalogs: List[str] = Field(alias="databricksListCatalogs")


ListDatabricksCatalogs.model_rebuild()
