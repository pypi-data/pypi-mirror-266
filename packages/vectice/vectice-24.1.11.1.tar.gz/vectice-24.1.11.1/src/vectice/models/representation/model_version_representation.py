from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict

from vectice.api.json.model_version import ModelVersionStatus
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput, ModelVersionUpdateInput
from vectice.models.attachment_container import AttachmentContainer
from vectice.models.metric import Metric
from vectice.models.property import Property
from vectice.utils.common_utils import (
    convert_list_keyvalue_to_dict,
    format_metrics,
    format_properties,
    repr_class,
    strip_dict_list,
)
from vectice.utils.dataframe_utils import repr_list_as_pd_dataframe

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pandas import DataFrame

    from vectice.api.client import Client


class ModelVersionRepresentation:
    """Represents the metadata of a Vectice model version.

    A Model Version Representation shows information about a specific version of a model from the Vectice app.
    It makes it easier to get and read this information through the API.

    NOTE: **Hint**
        A model version ID starts with 'MDV-XXX'. Retrieve the ID in the Vectice App, then use the ID with the following methods to get the model version:
        ```connect.model_version('MDV-XXX')``` or ```connect.browse('MDV-XXX')```
        (see [Connection page](https://api-docs.vectice.com/reference/vectice/connection/#vectice.Connection.model_version)).

    Attributes:
        id (str): The unique identifier of the model version.
        project_id (str): The identifier of the project to which the model version belongs.
        name (str): The name of the model version. For model versions it corresponds to the version number.
        status (str): The status of the model version (EXPERIMENTATION, STAGING, PRODUCTION, or RETIRED).
        description (str): The description of the model version.
        technique (str): The technique used by the model version.
        library (str): The library used by the model version.
        metrics (List[Dict[str, Any]]): The metrics associated with the model version.
        properties (List[Dict[str, Any]]): The properties associated with the model version.
        model_representation (ModelRepresentation): Holds informations about the source model linked to the model version, where all versions are grouped together.
    """

    def __init__(self, output: ModelVersionRepresentationOutput, client: Client):
        from vectice.models.representation.model_representation import ModelRepresentation

        self.id = output.id
        self.project_id = output.project_id
        self.name = output.name
        self.status = output.status
        self.description = output.description
        self.technique = output.technique
        self.library = output.library
        self.metrics = output.metrics
        self.properties = strip_dict_list(output.properties)
        self.model_representation = ModelRepresentation(output.model, client)

        self._client = client
        self._output = output

    def __repr__(self):
        return repr_class(self)

    def asdict(self) -> Dict[str, Any]:
        """Transform the ModelVersionRepresentation into a organised dictionary.

        Returns:
            The object represented as a dictionary
        """
        flat_metrics = convert_list_keyvalue_to_dict(self.metrics)
        flat_properties = convert_list_keyvalue_to_dict(self.properties)

        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,
            "status": self.status,
            "description": self.description,
            "technique": self.technique,
            "library": self.library,
            "metrics": flat_metrics,
            "properties": flat_properties,
            "model_representation": (self.model_representation.asdict() if self.model_representation else None),
        }

    def metrics_as_dataframe(self) -> DataFrame:
        """Transforms the metrics of the ModelVersionRepresentation into a DataFrame for better readability.

        Returns:
            A pandas DataFrame containing the metrics of the model version.
        """
        return repr_list_as_pd_dataframe(self.metrics)  # change key name

    def properties_as_dataframe(self) -> DataFrame:
        """Transforms the properties of the ModelVersionRepresentation into a DataFrame for better readability.

        Returns:
            A pandas DataFrame containing the properties of the model version.
        """
        return repr_list_as_pd_dataframe(self.properties)  # change key name

    def update(
        self,
        status: str | None = None,
        metrics: dict[str, int | float] | list[Metric] | Metric | None = None,
        properties: dict[str, str | int] | list[Property] | Property | None = None,
        attachments: str | list[str] | None = None,
    ) -> None:
        """Update the Model Version from the API.

        Parameters:
            status: The new status of the model. Accepted values are EXPERIMENTATION, STAGING, PRODUCTION and RETIRED.
            properties: The new properties of the model.
            metrics: The new metrics of the model.
            attachments: The new attachments of the model.

        Returns:
            None
        """
        if status is not None:
            self._update_status(status)

        if attachments is not None:
            self._update_attachments(attachments)

        if metrics is not None:
            self._upsert_metrics(metrics)

        if properties is not None:
            self._upsert_properties(properties)

    def _update_status(self, status: str):
        try:
            status_enum = ModelVersionStatus(status.strip().upper())
        except ValueError as err:
            accepted_statuses = ", ".join([f"{status_enum.value!r}" for status_enum in ModelVersionStatus])
            raise ValueError(f"'{status}' is an invalid value. Please use [{accepted_statuses}].") from err

        model_input = ModelVersionUpdateInput(status=status_enum.value)
        self._client.update_model(self.id, model_input)
        old_status = self.status
        self.status = status_enum.value
        _logger.info(f"Model version {self.id!r} transitioned from {old_status!r} to {self.status!r}.")

    def _upsert_properties(self, properties: dict[str, str | int] | list[Property] | Property):
        clean_properties = list(map(lambda property: property.key_val_dict(), format_properties(properties)))
        new_properties = self._client.upsert_properties("modelVersion", self.id, clean_properties)
        self.properties = strip_dict_list(new_properties)
        _logger.info(f"Model version {self.id!r} properties successfully updated.")

    def _upsert_metrics(self, metrics: dict[str, int | float] | list[Metric] | Metric):
        clean_metrics = list(map(lambda metric: metric.key_val_dict(), format_metrics(metrics)))
        self.metrics = self._client.upsert_metrics("modelVersion", self.id, clean_metrics)
        _logger.info(f"Model version {self.id!r} metrics successfully updated.")

    def _update_attachments(self, attachments: str | list[str]):
        container = AttachmentContainer(self._output, self._client)
        container.upsert_attachments(attachments)
        _logger.info(f"Model version {self.id!r} attachments successfully updated.")
