from vectice.api.json.dataset_representation import DatasetRepresentationOutput
from vectice.utils.common_utils import repr_class


class DatasetRepresentation:
    def __init__(self, output: DatasetRepresentationOutput):
        self.id = output.id
        self.project_id = output.project_id
        self.name = output.name
        self.type = output.type
        self.origin = output.origin
        self.description = output.description
        self._last_version = output.version

    def __repr__(self):
        return repr_class(self)

    def _asdict(self):
        return {
            "name": self.name,
            "id": self.id,
            "description": self.description,
            "type": self.type,
            "origin": self.origin,
        }
