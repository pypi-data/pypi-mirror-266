from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateWindowNamespace(BaseModel):
    window_namespace_update: "UpdateWindowNamespaceWindowNamespaceUpdate" = Field(
        alias="windowNamespaceUpdate"
    )


class UpdateWindowNamespaceWindowNamespaceUpdate(NamespaceUpdate):
    pass


UpdateWindowNamespace.model_rebuild()
UpdateWindowNamespaceWindowNamespaceUpdate.model_rebuild()
