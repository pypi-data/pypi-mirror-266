from __future__ import annotations

import logging
import mimetypes
import os
import pickle  # nosec
import re
from contextlib import contextmanager
from enum import Enum
from io import BufferedReader, BytesIO, IOBase
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Union

from gql.transport.exceptions import TransportQueryError
from PIL import Image, ImageFile
from rich.console import Console
from rich.table import Table

from vectice.api.http_error_handlers import VecticeException
from vectice.api.json.iteration import IterationStatus
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput
from vectice.api.json.step import StepOutput, StepType
from vectice.models.attachment_container import AttachmentContainer
from vectice.models.metric import Metric
from vectice.models.property import Property

if TYPE_CHECKING:
    from vectice.api.client import Client
    from vectice.api.json import AttachmentOutput
    from vectice.api.json.dataset_version import DatasetVersionOutput
    from vectice.api.json.model_version import ModelVersionOutput
    from vectice.models.dataset import Dataset
    from vectice.models.iteration import Iteration
    from vectice.models.model import Model
    from vectice.models.step import Step


@contextmanager
def hide_logs(package: str):
    old_level = logging.getLogger(package).level
    try:
        logging.getLogger(package).setLevel(logging.ERROR)
        yield
    finally:
        logging.getLogger(package).setLevel(old_level)


def check_read_only(iteration: Iteration):
    """Check if an iteration is completed or cancelled.

    Refreshing the iteration is necessary because in a Jupyter notebook
    its status could have changed on the backend.

    Parameters:
        iteration: The iteration to check.

    Raises:
        RuntimeError: When the iteration is read-only (completed or cancelled).
    """
    refresh_iteration = iteration._phase.iteration(iteration.index)  # pyright: ignore[reportPrivateUsage]
    if refresh_iteration._status in {  # pyright: ignore[reportPrivateUsage]
        IterationStatus.Completed,
        IterationStatus.Abandoned,
    }:
        raise RuntimeError(f"The Iteration is {refresh_iteration.status} and is read-only.")


def get_step_type(
    step_output: StepOutput,
    iteration: Iteration,
) -> Step:
    # TODO: cyclic imports
    from vectice.models.step import Step
    from vectice.models.step_dataset import StepDataset
    from vectice.models.step_image import StepImage
    from vectice.models.step_model import StepModel
    from vectice.models.step_number import StepNumber
    from vectice.models.step_string import StepString

    artifacts = step_output.artifacts
    step = Step(
        id=step_output.id,
        iteration=iteration,
        name=step_output.name,
        index=step_output.index,
        slug=step_output.slug,
        description=step_output.description,
        artifacts=artifacts,
        step_type=StepType.Step,
    )

    def _get_number(text: int | float | str):
        try:
            return float(text)
        except ValueError:
            return text

    if (
        artifacts is not None  # pyright: ignore[reportUnnecessaryIsInstance, reportUnnecessaryComparison]
        and len(artifacts) >= 1  # pyright: ignore[reportUnnecessaryIsInstance, reportUnnecessaryComparison]
    ):
        artifact = artifacts[len(artifacts) - 1]
        if artifact.dataset_version_id is not None:
            return StepDataset(step, artifact)
        if artifact.model_version_id is not None:
            return StepModel(step, artifact)
        if artifact.entity_file_id:
            image = _get_image_info(iteration, artifact.entity_file_id)
            return step if image is None else StepImage(step, image)
        if artifact.text:
            str_or_float = _get_number(artifact.text)
            return (
                StepNumber(step, str_or_float)
                if isinstance(str_or_float, float)
                else StepString(step, str(str_or_float))
            )
    return step


def _get_image_info(iteration: Iteration, entity_file_id: int):
    try:
        image = iteration._client.get_entity_file_by_id(entity_file_id)  # pyright: ignore[reportPrivateUsage]
        return image.file_name
    except TransportQueryError:
        return None


def check_image_path(path: str) -> bool:
    if _check_for_comment(path):
        return False
    try:
        check_path = Path(path).exists()
    except OSError:
        return False
    _, ext = os.path.splitext(path)
    pillow_extensions = {exten for exten in Image.registered_extensions()}
    if not check_path and ext in pillow_extensions:
        raise ValueError("Check the file path.")
    if ext not in pillow_extensions:
        return False
    return True


def check_file_path(path: str) -> bool:
    if _check_for_comment(path):
        return False
    try:
        check_image_path(path)
    except ValueError:
        raise ValueError("Check the file path.") from None
    _, ext = os.path.splitext(path)
    mime_type = mimetypes.guess_type(path)[0]
    if not mime_type and ext not in [".parquet", ".ipynb"]:
        return False
    return True


def _check_for_comment(path: str) -> bool:
    _, ext = os.path.splitext(path)
    if ext:
        return False
    return True


def _validate_image_or_file(path: str) -> BufferedReader:
    try:
        return open(path, "rb")
    except FileNotFoundError:
        raise ValueError(f"The provided file {path!r} cannot be opened. Check its format and permissions.") from None


def get_image_or_file_variables(value: str | IOBase | Image.Image) -> tuple[BufferedReader | IOBase | BytesIO, str]:
    if isinstance(value, IOBase):
        image = value
        filename = os.path.basename(value.name)  # type: ignore[attr-defined]
        return image, filename
    if isinstance(value, str):
        image = _validate_image_or_file(value)
        filename = os.path.basename(image.name)
        return image, filename
    if isinstance(value, Image.Image):  # pyright: ignore[reportUnnecessaryIsInstance]
        previous_load_truncated_images = ImageFile.LOAD_TRUNCATED_IMAGES
        previous_max_image_pixels = Image.MAX_IMAGE_PIXELS
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        Image.MAX_IMAGE_PIXELS = None
        in_mem_file = BytesIO()
        value.save(in_mem_file, format=value.format)
        in_mem_file.seek(0)
        filename = os.path.basename(value.filename)  # type: ignore #TODO I doubt filename really exists in PIL: https://stackoverflow.com/questions/45087638/get-image-filename-from-image-pil
        ImageFile.LOAD_TRUNCATED_IMAGES = previous_load_truncated_images
        Image.MAX_IMAGE_PIXELS = previous_max_image_pixels
        return in_mem_file, filename

    raise ValueError("Unsupported image provided.")


def temp_print(string: str | None = None, table: Table | None = None) -> None:
    console = Console(width=120)
    if string:
        print(string)
        print()
    if table:
        console.print(table)
        print()


def convert_keys_to_camel_case(input_dict: Dict[str, Any]) -> Dict[str, Union[Any, Dict[str, Any]]]:
    camel_case_dict: Dict[str, Union[Any, Dict[str, Any]]] = {}

    for key, value in input_dict.items():
        camel_case_key = re.sub(r"_([a-z])", lambda match: match.group(1).upper(), key)
        if isinstance(value, dict):
            value = convert_keys_to_camel_case(value)
        camel_case_dict[camel_case_key] = value

    return camel_case_dict


def format_attachments(attachments: str | list[str]) -> list[str]:
    list_attachments = (
        [attachment for attachment in set(attachments)] if isinstance(attachments, list) else [attachments]
    )
    for attachment in list_attachments:
        if not isinstance(attachment, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError(
                f"Argument 'attachments' with type '{type(attachment)}' is invalid, only str are supported."
            )
    return list_attachments


def check_string_sanity(value: str):
    if value == "":
        raise VecticeException("Cannot assign an empty comment. Please provide a valid comment")


def ensure_correct_project_id_from_representation_objs(project_id: str, value: Any):
    from vectice.models.representation.dataset_representation import DatasetRepresentation
    from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
    from vectice.models.representation.model_representation import ModelRepresentation
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation

    if (
        isinstance(value, DatasetRepresentation)
        or isinstance(value, DatasetVersionRepresentation)
        or isinstance(value, ModelRepresentation)
        or isinstance(value, ModelVersionRepresentation)
    ) and value.project_id != project_id:
        raise VecticeException("Assigning an asset coming from another project is forbidden")


def set_model_attachments(
    client: Client, model: Model, model_version: ModelVersionOutput
) -> tuple[list[AttachmentOutput] | None, bool]:
    logging.getLogger("vectice.models.attachment_container").propagate = True
    attachments = None
    if model.attachments:
        container = AttachmentContainer(model_version, client)
        attachments = container.upsert_attachments(model.attachments)

    success_pickle: bool = False
    if model.predictor is not None:
        try:
            model_content = _serialize_model(model.predictor)
            model_type_name = type(model.predictor).__name__
            container = AttachmentContainer(model_version, client)
            container.add_serialized_model(model_type_name, model_content)
            success_pickle = True
        except Exception:
            success_pickle = False

    return attachments, success_pickle


def set_dataset_attachments(client: Client, dataset: Dataset, dataset_version: DatasetVersionOutput):
    logging.getLogger("vectice.models.attachment_container").propagate = True
    attachments = None
    if dataset.attachments:
        container = AttachmentContainer(dataset_version, client)
        attachments = container.upsert_attachments(dataset.attachments)
    return attachments


def _serialize_model(model: Any) -> bytes:
    return pickle.dumps(model)


def repr_class(class_object: object) -> str:
    attributes = [
        (key, value.value if isinstance(value, Enum) else value)
        for key, value in vars(class_object).items()
        if not key.startswith("_")
    ]
    attribute_strings = [f"{key} = {value}" for key, value in attributes]
    return f'{class_object.__class__.__name__}({", ".join(attribute_strings)})'


def strip_dict_list(dict_list: List[Dict[str, str | int]]) -> List[Dict[str, str | int]]:
    cleaned_list = []
    for item in dict_list:
        if "value" in item:
            if isinstance(item["value"], str):
                cleaned_value = re.sub(r"\s{2,}", " ", item["value"].replace("\n", ""))
                item["value"] = cleaned_value

            cleaned_list.append(item)
    return cleaned_list


def remove_type_name(dict_list: List[ModelVersionRepresentationOutput]) -> List[ModelVersionRepresentationOutput]:
    for item in dict_list:
        if "__typename" in item:
            del item["__typename"]
    return dict_list


def convert_list_keyvalue_to_dict(list_kv: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {item["key"]: item["value"] for item in list_kv}


def process_versions_list_metrics_and_properties(
    dict_list: List[ModelVersionRepresentationOutput],
) -> List[Dict[str, Any]]:
    return_dict: List[Dict[str, Any]] = []

    for item in dict_list:
        if "metrics" in item:
            item["metrics"] = convert_list_keyvalue_to_dict(item["metrics"])
        if "properties" in item:
            item["properties"] = strip_dict_list(item["properties"])
            item["properties"] = convert_list_keyvalue_to_dict(item["properties"])
        return_dict.append(item)
    return return_dict


def flatten_dict(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    flattened_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flattened_dict[f"{key}_{sub_key}"] = sub_value
        else:
            flattened_dict[key] = value
    return flattened_dict


def convert_to_snake_case(key: str) -> str:
    snake_case_key = "".join(["_" + i.lower() if i.isupper() else i for i in key]).lstrip("_")
    return snake_case_key


def convert_keys_to_snake_case(dictionary: ModelVersionRepresentationOutput) -> ModelVersionRepresentationOutput:
    converted_dict: ModelVersionRepresentationOutput = ModelVersionRepresentationOutput({})
    for k, v in dictionary.items():
        if k == "vecticeId":
            converted_dict["id"] = v
        else:
            converted_dict[convert_to_snake_case(k)] = v
    return converted_dict


def format_metrics(metrics: dict[str, int | float] | list[Metric] | Metric | None) -> list[Metric]:
    if metrics is None:
        return []
    if isinstance(metrics, Metric):
        return [metrics]
    if isinstance(metrics, list):
        metrics = _remove_incorrect_metrics(metrics)
        key_list = [metric.key for metric in metrics]
        check_key_duplicates(key_list)
        return metrics
    if isinstance(metrics, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
        return [Metric(key, value) for (key, value) in metrics.items()]
    else:
        raise ValueError("Please check metric type.")


def format_properties(properties: dict[str, str | int] | list[Property] | Property | None) -> list[Property]:
    if properties is None:
        return []
    if isinstance(properties, Property):
        return [properties]
    if isinstance(properties, list):
        properties = _remove_incorrect_properties(properties)
        key_list = [prop.key for prop in properties]
        check_key_duplicates(key_list)
        return properties
    if isinstance(properties, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
        return [Property(key, str(value)) for (key, value) in properties.items()]
    else:
        raise ValueError("Please check property type.")


def check_key_duplicates(key_list: list[str]):
    if len(key_list) != len(set(key_list)):
        raise ValueError("Duplicate keys are not allowed.")


def _remove_incorrect_properties(properties: list[Property]) -> list[Property]:
    for prop in properties:
        if not isinstance(prop, Property):  # pyright: ignore[reportUnnecessaryIsInstance]
            logging.warning(f"Incorrect property '{prop}'. Please check property type.")
            properties.remove(prop)
    return properties


def _remove_incorrect_metrics(metrics: list[Metric]) -> list[Metric]:
    for metric in metrics:
        if not isinstance(metric, Metric):  # pyright: ignore[reportUnnecessaryIsInstance]
            logging.warning(f"Incorrect metric '{metric}'. Please check metric type.")
            metrics.remove(metric)
    return metrics
