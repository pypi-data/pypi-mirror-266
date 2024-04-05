from typing import List

from pydantic import Field

from .base_model import BaseModel


class ListDbtModelJobs(BaseModel):
    dbt_model_list_jobs: List[str] = Field(alias="dbtModelListJobs")


ListDbtModelJobs.model_rebuild()
