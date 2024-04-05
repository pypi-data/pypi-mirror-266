from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateUserNamespace(BaseModel):
    user_namespace_update: "UpdateUserNamespaceUserNamespaceUpdate" = Field(
        alias="userNamespaceUpdate"
    )


class UpdateUserNamespaceUserNamespaceUpdate(NamespaceUpdate):
    pass


UpdateUserNamespace.model_rebuild()
UpdateUserNamespaceUserNamespaceUpdate.model_rebuild()
