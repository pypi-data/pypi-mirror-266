from typing import List

from pydantic import Field

from .base_model import BaseModel


class ListDbtModelProjects(BaseModel):
    dbt_model_list_projects: List[str] = Field(alias="dbtModelListProjects")


ListDbtModelProjects.model_rebuild()
