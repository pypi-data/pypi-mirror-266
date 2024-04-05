from typing import List

from pydantic import Field

from .base_model import BaseModel


class ListResourceNamespaces(BaseModel):
    resource_namespaces_list: List[
        "ListResourceNamespacesResourceNamespacesList"
    ] = Field(alias="resourceNamespacesList")


class ListResourceNamespacesResourceNamespacesList(BaseModel):
    resource_namespace: str = Field(alias="resourceNamespace")


ListResourceNamespaces.model_rebuild()
ListResourceNamespacesResourceNamespacesList.model_rebuild()
