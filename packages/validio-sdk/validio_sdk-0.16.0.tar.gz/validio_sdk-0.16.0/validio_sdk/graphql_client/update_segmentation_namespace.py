from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateSegmentationNamespace(BaseModel):
    segmentation_namespace_update: "UpdateSegmentationNamespaceSegmentationNamespaceUpdate" = Field(
        alias="segmentationNamespaceUpdate"
    )


class UpdateSegmentationNamespaceSegmentationNamespaceUpdate(NamespaceUpdate):
    pass


UpdateSegmentationNamespace.model_rebuild()
UpdateSegmentationNamespaceSegmentationNamespaceUpdate.model_rebuild()
