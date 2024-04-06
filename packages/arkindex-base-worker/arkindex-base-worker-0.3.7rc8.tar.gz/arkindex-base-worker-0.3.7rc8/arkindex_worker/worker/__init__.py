"""
Base classes to implement Arkindex workers.
"""

import contextlib
import json
import os
import sys
import uuid
from argparse import ArgumentTypeError
from collections.abc import Iterable, Iterator
from enum import Enum
from pathlib import Path

from apistar.exceptions import ErrorResponse

from arkindex_worker import logger
from arkindex_worker.cache import CachedElement
from arkindex_worker.models import Dataset, Element, Set
from arkindex_worker.worker.base import BaseWorker
from arkindex_worker.worker.classification import ClassificationMixin
from arkindex_worker.worker.dataset import DatasetMixin, DatasetState
from arkindex_worker.worker.element import ElementMixin
from arkindex_worker.worker.entity import EntityMixin
from arkindex_worker.worker.metadata import MetaDataMixin, MetaType  # noqa: F401
from arkindex_worker.worker.task import TaskMixin
from arkindex_worker.worker.transcription import TranscriptionMixin
from arkindex_worker.worker.version import WorkerVersionMixin


class ActivityState(Enum):
    """
    Processing state of an element.
    """

    Queued = "queued"
    """
    The element has not yet been processed by a worker.
    """

    Started = "started"
    """
    The element is being processed by a worker.
    """

    Processed = "processed"
    """
    The element has been successfully processed by a worker.
    """

    Error = "error"
    """
    An error occurred while processing this element.
    """


class ElementsWorker(
    BaseWorker,
    ClassificationMixin,
    ElementMixin,
    TranscriptionMixin,
    WorkerVersionMixin,
    EntityMixin,
    MetaDataMixin,
):
    """
    Base class for ML workers that operate on Arkindex elements.

    This class inherits from numerous mixin classes found in other modules of
    ``arkindex.worker``, which provide helpers to read and write to the Arkindex API.
    """

    def __init__(
        self, description: str = "Arkindex Elements Worker", support_cache: bool = False
    ):
        """
        :param description: The worker's description
        :param support_cache: Whether the worker supports cache
        """
        super().__init__(description, support_cache)

        # Add mandatory argument to process elements
        self.parser.add_argument(
            "--elements-list",
            help="JSON elements list to use",
            type=open,
            default=os.environ.get("TASK_ELEMENTS"),
        )
        self.parser.add_argument(
            "--element",
            type=uuid.UUID,
            nargs="+",
            help="One or more Arkindex element ID",
        )

        self.classes = {}

        self.entity_types = {}
        """Known and available entity types in processed corpus
        """

        self._worker_version_cache = {}

    def list_elements(self) -> Iterable[CachedElement] | list[str]:
        """
        List the elements to be processed, either from the CLI arguments or
        the cache database when enabled.

        :return: An iterable of [CachedElement][arkindex_worker.cache.CachedElement] when cache support is enabled,
           and a list of strings representing element IDs otherwise.
        """
        assert not (
            self.args.elements_list and self.args.element
        ), "elements-list and element CLI args shouldn't be both set"
        out = []

        # Load from the cache when available
        # Flake8 wants us to use 'is True', but Peewee only supports '== True'
        cache_query = CachedElement.select().where(
            CachedElement.initial == True  # noqa: E712
        )
        if self.use_cache and cache_query.exists():
            return cache_query
        # Process elements from JSON file
        elif self.args.elements_list:
            data = json.load(self.args.elements_list)
            assert isinstance(data, list), "Elements list must be a list"
            assert len(data), "No elements in elements list"
            out += list(filter(None, [element.get("id") for element in data]))
        # Add any extra element from CLI
        elif self.args.element:
            out += self.args.element

        return out

    @property
    def store_activity(self) -> bool:
        """
        Whether or not WorkerActivity support has been enabled on the DataImport
        used to run this worker.
        """
        if self.is_read_only:
            return False
        assert (
            self.process_information
        ), "Worker must be configured to access its process activity state"
        return self.process_information.get("activity_state") == "ready"

    def configure(self):
        """
        Setup the worker using CLI arguments and environment variables.
        """
        # CLI args are stored on the instance so that implementations can access them
        self.args = self.parser.parse_args()

        if self.is_read_only:
            super().configure_for_developers()
        else:
            super().configure()
            super().configure_cache()

        # Retrieve the model configuration
        if self.model_configuration:
            self.config.update(self.model_configuration)
            logger.info("Model version configuration retrieved")

        # Retrieve the user configuration
        if self.user_configuration:
            self.config.update(self.user_configuration)
            logger.info("User configuration retrieved")

    def run(self):
        """
        Implements an Arkindex worker that goes through each element returned by
        [list_elements][arkindex_worker.worker.ElementsWorker.list_elements].
        It calls [process_element][arkindex_worker.worker.ElementsWorker.process_element],
        catching exceptions, and handles saving WorkerActivity updates when enabled.
        """
        self.configure()

        # List all elements either from JSON file
        # or direct list of elements on CLI
        elements = self.list_elements()
        if not elements:
            logger.warning("No elements to process, stopping.")
            sys.exit(1)

        if not self.store_activity:
            logger.info(
                "No worker activity will be stored as it is disabled for this process"
            )

        # Process every element
        count = len(elements)
        failed = 0
        for i, item in enumerate(elements, start=1):
            element = None
            try:
                if self.use_cache:
                    # Just use the result of list_elements as the element
                    element = item
                else:
                    # Load element using the Arkindex API
                    element = Element(**self.request("RetrieveElement", id=item))

                logger.info(f"Processing {element} ({i}/{count})")

                # Process the element and report its progress if activities are enabled
                if self.update_activity(element.id, ActivityState.Started):
                    self.process_element(element)
                    self.update_activity(element.id, ActivityState.Processed)
                else:
                    logger.info(
                        f"Skipping element {element.id} as it was already processed"
                    )
                    continue
            except Exception as e:
                # Handle errors occurring while retrieving, processing or patching the activity for this element.
                # Count the element as failed in case the activity update to "started" failed with no conflict.
                # This prevent from processing the element
                failed += 1

                # Handle the case where we failed retrieving the element
                element_id = element.id if element else item

                if isinstance(e, ErrorResponse):
                    message = f"An API error occurred while processing element {element_id}: {e.title} - {e.content}"
                else:
                    message = (
                        f"Failed running worker on element {element_id}: {repr(e)}"
                    )

                logger.warning(
                    message,
                    exc_info=e if self.args.verbose else None,
                )
                if element:
                    # Try to update the activity to error state regardless of the response
                    with contextlib.suppress(Exception):
                        self.update_activity(element.id, ActivityState.Error)

        message = f'Ran on {count} element{"s"[:count>1]}: {count - failed} completed, {failed} failed'
        if failed:
            logger.error(message)
            if failed >= count:  # Everything failed!
                sys.exit(1)
        else:
            logger.info(message)

    def process_element(self, element: Element | CachedElement):
        """
        Override this method to implement your worker and process a single Arkindex element at once.

        :param element: The element to process.
           Will be a CachedElement instance if cache support is enabled,
           and an Element instance otherwise.
        """

    def update_activity(
        self, element_id: str | uuid.UUID, state: ActivityState
    ) -> bool:
        """
        Update the WorkerActivity for this element and worker.

        :param element_id: ID of the element.
        :param state: New WorkerActivity state for this element.
        :returns: True if the update has been successful or WorkerActivity support is disabled.
           False if the update has failed due to a conflict; this worker might have already processed
           this element.
        """
        if not self.store_activity:
            logger.debug(
                "Activity is not stored as the feature is disabled on this process"
            )
            return True

        assert element_id and isinstance(
            element_id, uuid.UUID | str
        ), "element_id shouldn't be null and should be an UUID or str"
        assert isinstance(state, ActivityState), "state should be an ActivityState"

        try:
            self.request(
                "UpdateWorkerActivity",
                id=self.worker_run_id,
                body={
                    "element_id": str(element_id),
                    "process_id": self.process_information["id"],
                    "state": state.value,
                },
            )
        except ErrorResponse as e:
            if state == ActivityState.Started and e.status_code == 409:
                # 409 conflict error when updating the state of an activity to "started" mean that we
                # cannot process this element. We assume that the reason is that the state transition
                # was forbidden i.e. that the activity was already in a started or processed state.
                # This allow concurrent access to an element activity between multiple processes.
                # Element should not be counted as failed as it is probably handled somewhere else.
                logger.debug(
                    f"Cannot start processing element {element_id} due to a conflict. "
                    f"Another process could have processed it with the same version already."
                )
                return False
            logger.warning(
                f"Failed to update activity of element {element_id} to {state.value} due to an API error: {e.content}"
            )
            raise e

        logger.debug(f"Updated activity of element {element_id} to {state}")
        return True


def check_dataset_set(value: str) -> tuple[uuid.UUID, str]:
    values = value.split(":")
    if len(values) != 2:
        raise ArgumentTypeError(
            f"'{value}' is not in the correct format `<dataset_id>:<set_name>`"
        )

    dataset_id, set_name = values
    try:
        dataset_id = uuid.UUID(dataset_id)
        return (dataset_id, set_name)
    except (TypeError, ValueError) as e:
        raise ArgumentTypeError(f"'{dataset_id}' should be a valid UUID") from e


class MissingDatasetArchive(Exception):
    """
    Exception raised when the compressed archive associated to
    a dataset isn't found in its task artifacts.
    """


class DatasetWorker(BaseWorker, DatasetMixin, TaskMixin):
    """
    Base class for ML workers that operate on Arkindex dataset sets.

    This class inherits from numerous mixin classes found in other modules of
    ``arkindex.worker``, which provide helpers to read and write to the Arkindex API.
    """

    def __init__(
        self,
        description: str = "Arkindex Dataset Worker",
        support_cache: bool = False,
    ):
        """
        :param description: The worker's description.
        :param support_cache: Whether the worker supports cache.
        """
        super().__init__(description, support_cache)

        # Path to the dataset compressed archive (containing images and a SQLite database)
        # Set as an instance variable as dataset workers might use it to easily extract its content
        self.downloaded_dataset_artifact: Path | None = None

        self.parser.add_argument(
            "--set",
            type=check_dataset_set,
            nargs="+",
            help="""
                One or more Arkindex dataset sets, format is <dataset_uuid>:<set_name>
                (e.g.: "12341234-1234-1234-1234-123412341234:train")
            """,
            default=[],
        )

    def configure(self):
        """
        Setup the worker using CLI arguments and environment variables.
        """
        # CLI args are stored on the instance so that implementations can access them
        self.args = self.parser.parse_args()

        if self.is_read_only:
            super().configure_for_developers()
        else:
            super().configure()
            super().configure_cache()

        # Retrieve the model configuration
        if self.model_configuration:
            self.config.update(self.model_configuration)
            logger.info("Model version configuration retrieved")

        # Retrieve the user configuration
        if self.user_configuration:
            self.config.update(self.user_configuration)
            logger.info("User configuration retrieved")

    def cleanup_downloaded_artifact(self) -> None:
        """
        Cleanup the downloaded dataset artifact if any
        """
        if not self.downloaded_dataset_artifact:
            return

        self.downloaded_dataset_artifact.unlink(missing_ok=True)

    def download_dataset_artifact(self, dataset: Dataset) -> None:
        """
        Find and download the compressed archive artifact describing a dataset using
        the [list_artifacts][arkindex_worker.worker.task.TaskMixin.list_artifacts] and
        [download_artifact][arkindex_worker.worker.task.TaskMixin.download_artifact] methods.

        :param dataset: The dataset to retrieve the compressed archive artifact for.
        :raises MissingDatasetArchive: When the dataset artifact is not found.
        """
        extra_dir = self.find_extras_directory()
        archive = extra_dir / dataset.filepath
        if archive.exists():
            return

        # Cleanup the dataset artifact that was downloaded previously
        self.cleanup_downloaded_artifact()

        logger.info(f"Downloading artifact for {dataset}")
        task_id = uuid.UUID(dataset.task_id)
        for artifact in self.list_artifacts(task_id):
            if artifact.path != dataset.filepath:
                continue

            archive.write_bytes(self.download_artifact(task_id, artifact).read())
            self.downloaded_dataset_artifact = archive
            return

        raise MissingDatasetArchive(
            "The dataset compressed archive artifact was not found."
        )

    def process_set(self, set: Set):
        """
        Override this method to implement your worker and process a single Arkindex dataset set at once.

        :param set: The set to process.
        """

    def list_sets(self) -> Iterator[Set]:
        """
        List the sets to be processed, either from the CLI arguments or using the
        [list_process_sets][arkindex_worker.worker.dataset.DatasetMixin.list_process_sets] method.

        :returns: An iterator of ``Set`` objects.
        """
        if not self.is_read_only:
            yield from self.list_process_sets()

        datasets: dict[uuid.UUID, Dataset] = {}
        for dataset_id, set_name in self.args.set:
            # Retrieving dataset information is not already cached
            if dataset_id not in datasets:
                datasets[dataset_id] = Dataset(
                    **self.request("RetrieveDataset", id=dataset_id)
                )

            yield Set(name=set_name, dataset=datasets[dataset_id])

    def run(self):
        """
        Implements an Arkindex worker that goes through each dataset set returned by
        [list_sets][arkindex_worker.worker.DatasetWorker.list_sets].

        It calls [process_set][arkindex_worker.worker.DatasetWorker.process_set],
        catching exceptions.
        """
        self.configure()

        dataset_sets: list[Set] = list(self.list_sets())
        if not dataset_sets:
            logger.warning("No sets to process, stopping.")
            sys.exit(1)

        # Process every set
        count = len(dataset_sets)
        failed = 0
        for i, dataset_set in enumerate(dataset_sets, start=1):
            try:
                assert (
                    dataset_set.dataset.state == DatasetState.Complete.value
                ), "When processing a set, its dataset state should be Complete."

                logger.info(f"Retrieving data for {dataset_set} ({i}/{count})")
                self.download_dataset_artifact(dataset_set.dataset)

                logger.info(f"Processing {dataset_set} ({i}/{count})")
                self.process_set(dataset_set)
            except Exception as e:
                # Handle errors occurring while retrieving or processing this dataset set
                failed += 1

                if isinstance(e, ErrorResponse):
                    message = f"An API error occurred while processing {dataset_set}: {e.title} - {e.content}"
                else:
                    message = f"Failed running worker on {dataset_set}: {repr(e)}"

                logger.warning(message, exc_info=e if self.args.verbose else None)

        # Cleanup the latest downloaded dataset artifact
        self.cleanup_downloaded_artifact()

        message = f'Ran on {count} set{"s"[:count>1]}: {count - failed} completed, {failed} failed'
        if failed:
            logger.error(message)
            if failed >= count:  # Everything failed!
                sys.exit(1)
        else:
            logger.info(message)
