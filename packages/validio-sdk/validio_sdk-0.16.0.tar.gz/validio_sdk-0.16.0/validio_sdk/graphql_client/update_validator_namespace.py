from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateValidatorNamespace(BaseModel):
    validator_namespace_update: "UpdateValidatorNamespaceValidatorNamespaceUpdate" = (
        Field(alias="validatorNamespaceUpdate")
    )


class UpdateValidatorNamespaceValidatorNamespaceUpdate(NamespaceUpdate):
    pass


UpdateValidatorNamespace.model_rebuild()
UpdateValidatorNamespaceValidatorNamespaceUpdate.model_rebuild()
