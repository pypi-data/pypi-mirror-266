from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateSourceNamespace(BaseModel):
    source_namespace_update: "UpdateSourceNamespaceSourceNamespaceUpdate" = Field(
        alias="sourceNamespaceUpdate"
    )


class UpdateSourceNamespaceSourceNamespaceUpdate(NamespaceUpdate):
    pass


UpdateSourceNamespace.model_rebuild()
UpdateSourceNamespaceSourceNamespaceUpdate.model_rebuild()
