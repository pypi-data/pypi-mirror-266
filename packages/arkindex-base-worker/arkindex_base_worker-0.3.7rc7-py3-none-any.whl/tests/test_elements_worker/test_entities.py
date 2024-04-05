import json
import re
from uuid import UUID

import pytest
from apistar.exceptions import ErrorResponse
from responses import matchers

from arkindex_worker.cache import (
    CachedElement,
    CachedEntity,
    CachedTranscription,
    CachedTranscriptionEntity,
)
from arkindex_worker.models import Transcription
from arkindex_worker.worker.entity import MissingEntityType
from arkindex_worker.worker.transcription import TextOrientation

from . import BASE_API_CALLS


def test_create_entity_wrong_name(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_entity(
            name=None,
            type="person",
        )

    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_entity(
            name=1234,
            type="person",
        )


def test_create_entity_wrong_type(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="type shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_entity(
            name="Bob Bob",
            type=None,
        )

    with pytest.raises(
        AssertionError, match="type shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_entity(
            name="Bob Bob",
            type=1234,
        )


def test_create_entity_wrong_corpus(mock_elements_worker):
    # Triggering an error on metas param, not giving corpus should work since
    # ARKINDEX_CORPUS_ID environment variable is set on mock_elements_worker
    with pytest.raises(AssertionError, match="metas should be of type dict"):
        mock_elements_worker.create_entity(
            name="Bob Bob",
            type="person",
            metas="wrong metas",
        )


def test_create_entity_wrong_metas(mock_elements_worker):
    with pytest.raises(AssertionError, match="metas should be of type dict"):
        mock_elements_worker.create_entity(
            name="Bob Bob",
            type="person",
            metas="wrong metas",
        )


def test_create_entity_wrong_validated(mock_elements_worker):
    with pytest.raises(AssertionError, match="validated should be of type bool"):
        mock_elements_worker.create_entity(
            name="Bob Bob",
            type="person",
            validated="wrong validated",
        )


def test_create_entity_api_error(responses, mock_elements_worker):
    # Set one entity type
    mock_elements_worker.entity_types = {"person": "person-entity-type-id"}
    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_entity(
            name="Bob Bob",
            type="person",
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        ("POST", "http://testserver/api/v1/entity/"),
        ("POST", "http://testserver/api/v1/entity/"),
        ("POST", "http://testserver/api/v1/entity/"),
        ("POST", "http://testserver/api/v1/entity/"),
        ("POST", "http://testserver/api/v1/entity/"),
    ]


def test_create_entity(responses, mock_elements_worker):
    # Set one entity type
    mock_elements_worker.entity_types = {"person": "person-entity-type-id"}

    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/",
        status=200,
        json={"id": "12345678-1234-1234-1234-123456789123"},
    )

    entity_id = mock_elements_worker.create_entity(
        name="Bob Bob",
        type="person",
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/entity/"),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "name": "Bob Bob",
        "type_id": "person-entity-type-id",
        "metas": {},
        "validated": None,
        "corpus": "11111111-1111-1111-1111-111111111111",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    assert entity_id == "12345678-1234-1234-1234-123456789123"


def test_create_entity_missing_type(responses, mock_elements_worker):
    """
    Create entity with an unknown type will fail.
    """
    # Call to list entity types
    responses.add(
        responses.GET,
        "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/entity-types/",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": [
                {"id": "person-entity-type-id", "name": "person", "color": "00d1b2"}
            ],
        },
    )

    with pytest.raises(
        AssertionError, match="Entity type `new-entity` not found in the corpus."
    ):
        mock_elements_worker.create_entity(
            name="Bob Bob",
            type="new-entity",
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/entity-types/",
        ),
    ]


def test_create_entity_with_cache(responses, mock_elements_worker_with_cache):
    # Set one entity type
    mock_elements_worker_with_cache.entity_types = {"person": "person-entity-type-id"}
    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/",
        status=200,
        json={"id": "12345678-1234-1234-1234-123456789123"},
    )

    entity_id = mock_elements_worker_with_cache.create_entity(
        name="Bob Bob",
        type="person",
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/entity/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "name": "Bob Bob",
        "type_id": "person-entity-type-id",
        "metas": {},
        "validated": None,
        "corpus": "11111111-1111-1111-1111-111111111111",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    assert entity_id == "12345678-1234-1234-1234-123456789123"

    # Check that created entity was properly stored in SQLite cache
    assert list(CachedEntity.select()) == [
        CachedEntity(
            id=UUID("12345678-1234-1234-1234-123456789123"),
            type="person",
            name="Bob Bob",
            validated=False,
            metas={},
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        )
    ]


def test_create_transcription_entity_wrong_transcription(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="transcription shouldn't be null and should be a Transcription",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=None,
            entity="11111111-1111-1111-1111-111111111111",
            offset=5,
            length=10,
        )

    with pytest.raises(
        AssertionError,
        match="transcription shouldn't be null and should be a Transcription",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=1234,
            entity="11111111-1111-1111-1111-111111111111",
            offset=5,
            length=10,
        )


def test_create_transcription_entity_wrong_entity(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="entity shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            entity=None,
            offset=5,
            length=10,
        )

    with pytest.raises(
        AssertionError, match="entity shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            entity=1234,
            offset=5,
            length=10,
        )


def test_create_transcription_entity_wrong_offset(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="offset shouldn't be null and should be a positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            entity="11111111-1111-1111-1111-111111111111",
            offset=None,
            length=10,
        )

    with pytest.raises(
        AssertionError,
        match="offset shouldn't be null and should be a positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            entity="11111111-1111-1111-1111-111111111111",
            offset="not an int",
            length=10,
        )

    with pytest.raises(
        AssertionError,
        match="offset shouldn't be null and should be a positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            entity="11111111-1111-1111-1111-111111111111",
            offset=-1,
            length=10,
        )


def test_create_transcription_entity_wrong_length(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="length shouldn't be null and should be a strictly positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            entity="11111111-1111-1111-1111-111111111111",
            offset=5,
            length=None,
        )

    with pytest.raises(
        AssertionError,
        match="length shouldn't be null and should be a strictly positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            entity="11111111-1111-1111-1111-111111111111",
            offset=5,
            length="not an int",
        )

    with pytest.raises(
        AssertionError,
        match="length shouldn't be null and should be a strictly positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            entity="11111111-1111-1111-1111-111111111111",
            offset=5,
            length=0,
        )


def test_create_transcription_entity_api_error(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            entity="11111111-1111-1111-1111-111111111111",
            offset=5,
            length=10,
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        ),
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        ),
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        ),
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        ),
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        ),
    ]


def test_create_transcription_entity_no_confidence(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        status=200,
        json={
            "entity": "11111111-1111-1111-1111-111111111111",
            "offset": 5,
            "length": 10,
        },
    )

    mock_elements_worker.create_transcription_entity(
        transcription=Transcription(
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "element": {"id": "myelement"},
            }
        ),
        entity="11111111-1111-1111-1111-111111111111",
        offset=5,
        length=10,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "entity": "11111111-1111-1111-1111-111111111111",
        "offset": 5,
        "length": 10,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }


def test_create_transcription_entity_with_confidence(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        status=200,
        json={
            "entity": "11111111-1111-1111-1111-111111111111",
            "offset": 5,
            "length": 10,
            "confidence": 0.33,
        },
    )

    mock_elements_worker.create_transcription_entity(
        transcription=Transcription(
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "element": {"id": "myelement"},
            }
        ),
        entity="11111111-1111-1111-1111-111111111111",
        offset=5,
        length=10,
        confidence=0.33,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "entity": "11111111-1111-1111-1111-111111111111",
        "offset": 5,
        "length": 10,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.33,
    }


def test_create_transcription_entity_confidence_none(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        status=200,
        json={
            "entity": "11111111-1111-1111-1111-111111111111",
            "offset": 5,
            "length": 10,
            "confidence": None,
        },
    )

    mock_elements_worker.create_transcription_entity(
        transcription=Transcription(
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "element": {"id": "myelement"},
            }
        ),
        entity="11111111-1111-1111-1111-111111111111",
        offset=5,
        length=10,
        confidence=None,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "entity": "11111111-1111-1111-1111-111111111111",
        "offset": 5,
        "length": 10,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }


def test_create_transcription_entity_with_cache(
    responses, mock_elements_worker_with_cache
):
    CachedElement.create(
        id=UUID("12341234-1234-1234-1234-123412341234"),
        type="page",
    )
    CachedTranscription.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        element=UUID("12341234-1234-1234-1234-123412341234"),
        text="Hello, it's me.",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedEntity.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        type="person",
        name="Bob Bob",
        worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
    )

    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        status=200,
        json={
            "entity": "11111111-1111-1111-1111-111111111111",
            "offset": 5,
            "length": 10,
        },
    )

    mock_elements_worker_with_cache.create_transcription_entity(
        transcription=Transcription(
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "element": {"id": "myelement"},
            }
        ),
        entity="11111111-1111-1111-1111-111111111111",
        offset=5,
        length=10,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "entity": "11111111-1111-1111-1111-111111111111",
        "offset": 5,
        "length": 10,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    # Check that created transcription entity was properly stored in SQLite cache
    assert list(CachedTranscriptionEntity.select()) == [
        CachedTranscriptionEntity(
            transcription=UUID("11111111-1111-1111-1111-111111111111"),
            entity=UUID("11111111-1111-1111-1111-111111111111"),
            offset=5,
            length=10,
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        )
    ]


def test_create_transcription_entity_with_confidence_with_cache(
    responses, mock_elements_worker_with_cache
):
    CachedElement.create(
        id=UUID("12341234-1234-1234-1234-123412341234"),
        type="page",
    )
    CachedTranscription.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        element=UUID("12341234-1234-1234-1234-123412341234"),
        text="Hello, it's me.",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedEntity.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        type="person",
        name="Bob Bob",
        worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
    )

    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        status=200,
        json={
            "entity": "11111111-1111-1111-1111-111111111111",
            "offset": 5,
            "length": 10,
            "confidence": 0.77,
        },
    )

    mock_elements_worker_with_cache.create_transcription_entity(
        transcription=Transcription(
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "element": {"id": "myelement"},
            }
        ),
        entity="11111111-1111-1111-1111-111111111111",
        offset=5,
        length=10,
        confidence=0.77,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entity/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "entity": "11111111-1111-1111-1111-111111111111",
        "offset": 5,
        "length": 10,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.77,
    }

    # Check that created transcription entity was properly stored in SQLite cache
    assert list(CachedTranscriptionEntity.select()) == [
        CachedTranscriptionEntity(
            transcription=UUID("11111111-1111-1111-1111-111111111111"),
            entity=UUID("11111111-1111-1111-1111-111111111111"),
            offset=5,
            length=10,
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
            confidence=0.77,
        )
    ]


def test_list_transcription_entities_deprecation(fake_dummy_worker):
    transcription = Transcription({"id": "fake_transcription_id"})
    worker_version = "worker_version_id"
    fake_dummy_worker.api_client.add_response(
        "ListTranscriptionEntities",
        id=transcription.id,
        worker_version=worker_version,
        response={"id": "entity_id"},
    )
    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        assert fake_dummy_worker.list_transcription_entities(
            transcription, worker_version=worker_version
        ) == {"id": "entity_id"}

    assert len(fake_dummy_worker.api_client.history) == 1
    assert len(fake_dummy_worker.api_client.responses) == 0


def test_list_transcription_entities(fake_dummy_worker):
    transcription = Transcription({"id": "fake_transcription_id"})
    worker_run = "worker_run_id"
    fake_dummy_worker.api_client.add_response(
        "ListTranscriptionEntities",
        id=transcription.id,
        worker_run=worker_run,
        response={"id": "entity_id"},
    )
    assert fake_dummy_worker.list_transcription_entities(
        transcription, worker_run=worker_run
    ) == {"id": "entity_id"}

    assert len(fake_dummy_worker.api_client.history) == 1
    assert len(fake_dummy_worker.api_client.responses) == 0


def test_list_corpus_entities(responses, mock_elements_worker):
    corpus_id = "11111111-1111-1111-1111-111111111111"
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{corpus_id}/entities/",
        json={
            "count": 1,
            "next": None,
            "results": [
                {
                    "id": "fake_entity_id",
                }
            ],
        },
    )

    mock_elements_worker.list_corpus_entities()

    assert mock_elements_worker.entities == {
        "fake_entity_id": {
            "id": "fake_entity_id",
        }
    }

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            f"http://testserver/api/v1/corpus/{corpus_id}/entities/",
        ),
    ]


@pytest.mark.parametrize("wrong_name", [1234, 12.5])
def test_list_corpus_entities_wrong_name(mock_elements_worker, wrong_name):
    with pytest.raises(AssertionError, match="name should be of type str"):
        mock_elements_worker.list_corpus_entities(name=wrong_name)


@pytest.mark.parametrize("wrong_parent", [{"id": "element_id"}, 12.5, "blabla"])
def test_list_corpus_entities_wrong_parent(mock_elements_worker, wrong_parent):
    with pytest.raises(AssertionError, match="parent should be of type Element"):
        mock_elements_worker.list_corpus_entities(parent=wrong_parent)


def test_check_required_entity_types(responses, mock_elements_worker):
    # Set one entity type
    mock_elements_worker.entity_types = {"person": "person-entity-type-id"}

    checked_types = ["person", "new-entity"]

    # Call to create new entity type
    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/types/",
        status=200,
        match=[
            matchers.json_params_matcher(
                {
                    "name": "new-entity",
                    "corpus": "11111111-1111-1111-1111-111111111111",
                }
            )
        ],
        json={
            "id": "new-entity-id",
            "corpus": "11111111-1111-1111-1111-111111111111",
            "name": "new-entity",
            "color": "ffd1b3",
        },
    )

    mock_elements_worker.check_required_entity_types(
        entity_types=checked_types,
    )

    # Make sure the entity_types entry has been updated
    assert mock_elements_worker.entity_types == {
        "person": "person-entity-type-id",
        "new-entity": "new-entity-id",
    }

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/entity/types/",
        ),
    ]


def test_check_required_entity_types_no_creation_allowed(
    responses, mock_elements_worker
):
    # Set one entity type
    mock_elements_worker.entity_types = {"person": "person-entity-type-id"}

    checked_types = ["person", "new-entity"]

    with pytest.raises(
        MissingEntityType, match="Entity type `new-entity` was not in the corpus."
    ):
        mock_elements_worker.check_required_entity_types(
            entity_types=checked_types, create_missing=False
        )

    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


@pytest.mark.parametrize("transcription", [None, "not a transcription", 1])
def test_create_transcription_entities_wrong_transcription(
    mock_elements_worker, transcription
):
    with pytest.raises(
        AssertionError,
        match="transcription shouldn't be null and should be of type Transcription",
    ):
        mock_elements_worker.create_transcription_entities(
            transcription=transcription,
            entities=[],
        )


@pytest.mark.parametrize(
    ("entities", "error"),
    [
        (None, "entities shouldn't be null and should be of type list"),
        (
            "not a list of entities",
            "entities shouldn't be null and should be of type list",
        ),
        (1, "entities shouldn't be null and should be of type list"),
        (
            [
                {
                    "name": "A",
                    "type_id": "12341234-1234-1234-1234-123412341234",
                    "offset": 0,
                    "length": 1,
                    "confidence": 0.5,
                }
            ]
            * 2,
            "entities should be unique",
        ),
    ],
)
def test_create_transcription_entities_wrong_entities(
    mock_elements_worker, entities, error
):
    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.create_transcription_entities(
            transcription=Transcription(id="transcription_id"),
            entities=entities,
        )


def test_create_transcription_entities_wrong_entities_subtype(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="Entity at index 0 in entities: Should be of type dict"
    ):
        mock_elements_worker.create_transcription_entities(
            transcription=Transcription(id="transcription_id"),
            entities=["not a dict"],
        )


@pytest.mark.parametrize(
    ("entity", "error"),
    [
        (
            {
                "name": None,
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": 0,
                "length": 1,
                "confidence": 0.5,
            },
            "Entity at index 0 in entities: name shouldn't be null and should be of type str",
        ),
        (
            {"name": "A", "type_id": None, "offset": 0, "length": 1, "confidence": 0.5},
            "Entity at index 0 in entities: type_id shouldn't be null and should be of type str",
        ),
        (
            {"name": "A", "type_id": 0, "offset": 0, "length": 1, "confidence": 0.5},
            "Entity at index 0 in entities: type_id shouldn't be null and should be of type str",
        ),
        (
            {
                "name": "A",
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": None,
                "length": 1,
                "confidence": 0.5,
            },
            "Entity at index 0 in entities: offset shouldn't be null and should be a positive integer",
        ),
        (
            {
                "name": "A",
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": -2,
                "length": 1,
                "confidence": 0.5,
            },
            "Entity at index 0 in entities: offset shouldn't be null and should be a positive integer",
        ),
        (
            {
                "name": "A",
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": 0,
                "length": None,
                "confidence": 0.5,
            },
            "Entity at index 0 in entities: length shouldn't be null and should be a strictly positive integer",
        ),
        (
            {
                "name": "A",
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": 0,
                "length": 0,
                "confidence": 0.5,
            },
            "Entity at index 0 in entities: length shouldn't be null and should be a strictly positive integer",
        ),
        (
            {
                "name": "A",
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": 0,
                "length": 1,
                "confidence": "not None or a float",
            },
            "Entity at index 0 in entities: confidence should be None or a float in [0..1] range",
        ),
        (
            {
                "name": "A",
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": 0,
                "length": 1,
                "confidence": 1.3,
            },
            "Entity at index 0 in entities: confidence should be None or a float in [0..1] range",
        ),
    ],
)
def test_create_transcription_entities_wrong_entity(
    mock_elements_worker, entity, error
):
    with pytest.raises(AssertionError, match=re.escape(error)):
        mock_elements_worker.create_transcription_entities(
            transcription=Transcription(id="transcription_id"),
            entities=[entity],
        )


def test_create_transcription_entities(responses, mock_elements_worker):
    transcription = Transcription(id="transcription-id")
    # Call to Transcription entities creation in bulk
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/transcription-id/entities/bulk/",
        status=201,
        match=[
            matchers.json_params_matcher(
                {
                    "worker_run_id": "56785678-5678-5678-5678-567856785678",
                    "entities": [
                        {
                            "name": "Teklia",
                            "type_id": "22222222-2222-2222-2222-222222222222",
                            "offset": 0,
                            "length": 6,
                            "confidence": 1.0,
                        }
                    ],
                }
            )
        ],
        json={
            "entities": [
                {
                    "transcription_entity_id": "transc-entity-id",
                    "entity_id": "entity-id",
                }
            ]
        },
    )

    # Store entity type/slug correspondence on the worker
    mock_elements_worker.entity_types = {
        "22222222-2222-2222-2222-222222222222": "organization"
    }
    created_objects = mock_elements_worker.create_transcription_entities(
        transcription=transcription,
        entities=[
            {
                "name": "Teklia",
                "type_id": "22222222-2222-2222-2222-222222222222",
                "offset": 0,
                "length": 6,
                "confidence": 1.0,
            }
        ],
    )

    assert len(created_objects) == 1

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/transcription-id/entities/bulk/",
        ),
    ]
