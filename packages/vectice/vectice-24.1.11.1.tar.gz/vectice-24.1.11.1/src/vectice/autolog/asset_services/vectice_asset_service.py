from __future__ import annotations

from typing import TypedDict, TypeVar

from vectice.models.dataset import Dataset
from vectice.models.model import Model
from vectice.models.table import Table

VecticeObjectTypes = TypeVar("VecticeObjectTypes", Dataset, Model, Table)
TVecticeObjects = TypedDict(
    "TVecticeObjects",
    {"variable": str, "vectice_object": VecticeObjectTypes},
)
VecticeObjectClasses = (Dataset, Model, Table)


class AutologVecticeAssetService:
    def __init__(self, key: str, asset: VecticeObjectTypes):
        self._asset = asset
        self._key = key

    def get_asset(self):
        return {
            "variable": self._key,
            "vectice_object": self._asset,
        }
