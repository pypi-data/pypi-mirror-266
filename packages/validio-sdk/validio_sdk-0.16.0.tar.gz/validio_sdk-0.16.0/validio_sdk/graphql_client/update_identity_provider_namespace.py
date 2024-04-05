from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateIdentityProviderNamespace(BaseModel):
    identity_provider_namespace_update: "UpdateIdentityProviderNamespaceIdentityProviderNamespaceUpdate" = Field(
        alias="identityProviderNamespaceUpdate"
    )


class UpdateIdentityProviderNamespaceIdentityProviderNamespaceUpdate(NamespaceUpdate):
    pass


UpdateIdentityProviderNamespace.model_rebuild()
UpdateIdentityProviderNamespaceIdentityProviderNamespaceUpdate.model_rebuild()
