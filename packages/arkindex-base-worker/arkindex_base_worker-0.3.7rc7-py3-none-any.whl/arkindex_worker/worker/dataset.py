"""
BaseWorker methods for datasets.
"""

from collections.abc import Iterator
from enum import Enum

from arkindex_worker import logger
from arkindex_worker.cache import unsupported_cache
from arkindex_worker.models import Dataset, Element, Set


class DatasetState(Enum):
    """
    State of a dataset.
    """

    Open = "open"
    """
    The dataset is open.
    """

    Building = "building"
    """
    The dataset is being built.
    """

    Complete = "complete"
    """
    The dataset is complete.
    """

    Error = "error"
    """
    The dataset is in error.
    """


class DatasetMixin:
    def list_process_sets(self) -> Iterator[Set]:
        """
        List dataset sets associated to the worker's process. This helper is not available in developer mode.

        :returns: An iterator of ``Set`` objects built from the ``ListProcessSets`` API endpoint.
        """
        assert not self.is_read_only, "This helper is not available in read-only mode."

        results = self.api_client.paginate(
            "ListProcessSets", id=self.process_information["id"]
        )

        return map(
            lambda result: Set(
                name=result["set_name"], dataset=Dataset(**result["dataset"])
            ),
            results,
        )

    def list_set_elements(self, dataset_set: Set) -> Iterator[Element]:
        """
        List elements in a dataset set.

        :param dataset_set: Set to find elements in.
        :returns: An iterator of Element built from the ``ListDatasetElements`` API endpoint.
        """
        assert dataset_set and isinstance(
            dataset_set, Set
        ), "dataset_set shouldn't be null and should be a Set"

        results = self.api_client.paginate(
            "ListDatasetElements", id=dataset_set.dataset.id, set=dataset_set.name
        )

        return map(lambda result: Element(**result["element"]), results)

    @unsupported_cache
    def update_dataset_state(self, dataset: Dataset, state: DatasetState) -> Dataset:
        """
        Partially updates a dataset state through the API.

        :param dataset: The dataset to update.
        :param state: State of the dataset.
        :returns: The updated ``Dataset`` object from the ``PartialUpdateDataset`` API endpoint.
        """
        assert dataset and isinstance(
            dataset, Dataset
        ), "dataset shouldn't be null and should be a Dataset"
        assert state and isinstance(
            state, DatasetState
        ), "state shouldn't be null and should be a str from DatasetState"

        if self.is_read_only:
            logger.warning("Cannot update dataset as this worker is in read-only mode")
            return

        updated_dataset = self.request(
            "PartialUpdateDataset",
            id=dataset.id,
            body={"state": state.value},
        )
        dataset.update(updated_dataset)

        return dataset
