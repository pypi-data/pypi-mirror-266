import json
import re
from argparse import Namespace
from uuid import UUID

import pytest
from apistar.exceptions import ErrorResponse
from responses import matchers

from arkindex_worker.cache import (
    SQL_VERSION,
    CachedElement,
    CachedImage,
    create_version_table,
    init_cache_db,
)
from arkindex_worker.models import Element
from arkindex_worker.worker import ElementsWorker
from arkindex_worker.worker.element import MissingTypeError

from . import BASE_API_CALLS


def test_check_required_types_argument_types(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="At least one element type slug is required."
    ):
        mock_elements_worker.check_required_types()

    with pytest.raises(AssertionError, match="Element type slugs must be strings."):
        mock_elements_worker.check_required_types("lol", 42)


def test_check_required_types(responses, mock_elements_worker):
    corpus_id = "11111111-1111-1111-1111-111111111111"
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{corpus_id}/",
        json={
            "id": corpus_id,
            "name": "Some Corpus",
            "types": [{"slug": "folder"}, {"slug": "page"}],
        },
    )
    mock_elements_worker.setup_api_client()

    assert mock_elements_worker.check_required_types("page")
    assert mock_elements_worker.check_required_types("page", "folder")

    with pytest.raises(
        MissingTypeError,
        match=re.escape(
            "Element type(s) act, text_line were not found in the Some Corpus corpus (11111111-1111-1111-1111-111111111111)."
        ),
    ):
        assert mock_elements_worker.check_required_types("page", "text_line", "act")


def test_create_missing_types(responses, mock_elements_worker):
    corpus_id = "11111111-1111-1111-1111-111111111111"

    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{corpus_id}/",
        json={
            "id": corpus_id,
            "name": "Some Corpus",
            "types": [{"slug": "folder"}, {"slug": "page"}],
        },
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/type/",
        match=[
            matchers.json_params_matcher(
                {
                    "slug": "text_line",
                    "display_name": "text_line",
                    "folder": False,
                    "corpus": corpus_id,
                }
            )
        ],
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/type/",
        match=[
            matchers.json_params_matcher(
                {
                    "slug": "act",
                    "display_name": "act",
                    "folder": False,
                    "corpus": corpus_id,
                }
            )
        ],
    )
    mock_elements_worker.setup_api_client()

    assert mock_elements_worker.check_required_types(
        "page", "text_line", "act", create_missing=True
    )


def test_list_elements_elements_list_arg_wrong_type(
    monkeypatch, tmp_path, mock_elements_worker
):
    elements_path = tmp_path / "elements.json"
    elements_path.write_text("{}")

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    with pytest.raises(AssertionError, match="Elements list must be a list"):
        worker.list_elements()


def test_list_elements_elements_list_arg_empty_list(
    monkeypatch, tmp_path, mock_elements_worker
):
    elements_path = tmp_path / "elements.json"
    elements_path.write_text("[]")

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    with pytest.raises(AssertionError, match="No elements in elements list"):
        worker.list_elements()


def test_list_elements_elements_list_arg_missing_id(
    monkeypatch, tmp_path, mock_elements_worker
):
    elements_path = tmp_path / "elements.json"
    with elements_path.open("w") as f:
        json.dump([{"type": "volume"}], f)

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    elt_list = worker.list_elements()

    assert elt_list == []


def test_list_elements_elements_list_arg(monkeypatch, tmp_path, mock_elements_worker):
    elements_path = tmp_path / "elements.json"
    with elements_path.open("w") as f:
        json.dump(
            [
                {"id": "volumeid", "type": "volume"},
                {"id": "pageid", "type": "page"},
                {"id": "actid", "type": "act"},
                {"id": "surfaceid", "type": "surface"},
            ],
            f,
        )

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    elt_list = worker.list_elements()

    assert elt_list == ["volumeid", "pageid", "actid", "surfaceid"]


def test_list_elements_element_arg(mocker, mock_elements_worker):
    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=["volumeid", "pageid"],
            verbose=False,
            elements_list=None,
            database=None,
            dev=False,
        ),
    )

    worker = ElementsWorker()
    worker.configure()

    elt_list = worker.list_elements()

    assert elt_list == ["volumeid", "pageid"]


def test_list_elements_both_args_error(mocker, mock_elements_worker, tmp_path):
    elements_path = tmp_path / "elements.json"
    with elements_path.open("w") as f:
        json.dump(
            [
                {"id": "volumeid", "type": "volume"},
                {"id": "pageid", "type": "page"},
                {"id": "actid", "type": "act"},
                {"id": "surfaceid", "type": "surface"},
            ],
            f,
        )
    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=["anotherid", "againanotherid"],
            verbose=False,
            elements_list=elements_path.open(),
            database=None,
            dev=False,
        ),
    )

    worker = ElementsWorker()
    worker.configure()

    with pytest.raises(
        AssertionError, match="elements-list and element CLI args shouldn't be both set"
    ):
        worker.list_elements()


def test_database_arg(mocker, mock_elements_worker, tmp_path):
    database_path = tmp_path / "my_database.sqlite"
    init_cache_db(database_path)
    create_version_table()

    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=["volumeid", "pageid"],
            verbose=False,
            elements_list=None,
            database=database_path,
            dev=False,
        ),
    )

    worker = ElementsWorker(support_cache=True)
    worker.configure()

    assert worker.use_cache is True
    assert worker.cache_path == database_path


def test_database_arg_cache_missing_version_table(
    mocker, mock_elements_worker, tmp_path
):
    database_path = tmp_path / "my_database.sqlite"
    database_path.touch()

    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=["volumeid", "pageid"],
            verbose=False,
            elements_list=None,
            database=database_path,
            dev=False,
        ),
    )

    worker = ElementsWorker(support_cache=True)
    with pytest.raises(
        AssertionError,
        match=f"The SQLite database {database_path} does not have the correct cache version, it should be {SQL_VERSION}",
    ):
        worker.configure()


def test_load_corpus_classes_api_error(responses, mock_elements_worker):
    responses.add(
        responses.GET,
        "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/classes/",
        status=500,
    )

    assert not mock_elements_worker.classes
    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        mock_elements_worker.load_corpus_classes()

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We do 5 retries
        (
            "GET",
            "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/classes/",
        ),
        (
            "GET",
            "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/classes/",
        ),
        (
            "GET",
            "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/classes/",
        ),
        (
            "GET",
            "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/classes/",
        ),
        (
            "GET",
            "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/classes/",
        ),
    ]
    assert not mock_elements_worker.classes


def test_load_corpus_classes(responses, mock_elements_worker):
    responses.add(
        responses.GET,
        "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/classes/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": [
                {
                    "id": "0000",
                    "name": "good",
                },
                {
                    "id": "1111",
                    "name": "average",
                },
                {
                    "id": "2222",
                    "name": "bad",
                },
            ],
        },
    )

    assert not mock_elements_worker.classes
    mock_elements_worker.load_corpus_classes()

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/classes/",
        ),
    ]
    assert mock_elements_worker.classes == {
        "good": "0000",
        "average": "1111",
        "bad": "2222",
    }


def test_create_sub_element_wrong_element(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="element shouldn't be null and should be of type Element"
    ):
        mock_elements_worker.create_sub_element(
            element=None,
            type="something",
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )

    with pytest.raises(
        AssertionError, match="element shouldn't be null and should be of type Element"
    ):
        mock_elements_worker.create_sub_element(
            element="not element type",
            type="something",
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )


def test_create_sub_element_wrong_type(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(
        AssertionError, match="type shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type=None,
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )

    with pytest.raises(
        AssertionError, match="type shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type=1234,
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )


def test_create_sub_element_wrong_name(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name=None,
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )

    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name=1234,
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )


def test_create_sub_element_wrong_polygon(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(AssertionError, match="polygon should be None or a list"):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon="not a polygon",
        )

    with pytest.raises(
        AssertionError, match="polygon should have at least three points"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[[1, 1], [2, 2]],
        )

    with pytest.raises(
        AssertionError, match="polygon points should be lists of two items"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[[1, 1, 1], [2, 2, 1], [2, 1, 1], [1, 2, 1]],
        )

    with pytest.raises(
        AssertionError, match="polygon points should be lists of two items"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[[1], [2], [2], [1]],
        )

    with pytest.raises(
        AssertionError, match="polygon points should be lists of two numbers"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[["not a coord", 1], [2, 2], [2, 1], [1, 2]],
        )


@pytest.mark.parametrize("confidence", ["lol", "0.2", -1.0, 1.42, float("inf")])
def test_create_sub_element_wrong_confidence(mock_elements_worker, confidence):
    with pytest.raises(
        AssertionError,
        match=re.escape("confidence should be None or a float in [0..1] range"),
    ):
        mock_elements_worker.create_sub_element(
            element=Element({"zone": None}),
            type="something",
            name="blah",
            polygon=[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
            confidence=confidence,
        )


@pytest.mark.parametrize(
    ("image", "error_type", "error_message"),
    [
        (1, AssertionError, "image should be None or string"),
        ("not a uuid", ValueError, "image is not a valid uuid."),
    ],
)
def test_create_sub_element_wrong_image(
    mock_elements_worker, image, error_type, error_message
):
    with pytest.raises(error_type, match=re.escape(error_message)):
        mock_elements_worker.create_sub_element(
            element=Element({"zone": None}),
            type="something",
            name="blah",
            polygon=[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
            image=image,
        )


def test_create_sub_element_wrong_image_and_polygon(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "An image or a parent with an image is required to create an element with a polygon."
        ),
    ):
        mock_elements_worker.create_sub_element(
            element=Element({"zone": None}),
            type="something",
            name="blah",
            polygon=[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
            image=None,
        )


def test_create_sub_element_api_error(responses, mock_elements_worker):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "corpus": {"id": "11111111-1111-1111-1111-111111111111"},
            "zone": {"image": {"id": "22222222-2222-2222-2222-222222222222"}},
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/create/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        ("POST", "http://testserver/api/v1/elements/create/"),
        ("POST", "http://testserver/api/v1/elements/create/"),
        ("POST", "http://testserver/api/v1/elements/create/"),
        ("POST", "http://testserver/api/v1/elements/create/"),
        ("POST", "http://testserver/api/v1/elements/create/"),
    ]


@pytest.mark.parametrize("slim_output", [True, False])
def test_create_sub_element(responses, mock_elements_worker, slim_output):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "corpus": {"id": "11111111-1111-1111-1111-111111111111"},
            "zone": {"image": {"id": "22222222-2222-2222-2222-222222222222"}},
        }
    )
    child_elt = {
        "id": "12345678-1234-1234-1234-123456789123",
        "corpus": {"id": "11111111-1111-1111-1111-111111111111"},
        "zone": {"image": {"id": "22222222-2222-2222-2222-222222222222"}},
    }
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/create/",
        status=200,
        json=child_elt,
    )

    element_creation_response = mock_elements_worker.create_sub_element(
        element=elt,
        type="something",
        name="0",
        polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        slim_output=slim_output,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/elements/create/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type": "something",
        "name": "0",
        "image": None,
        "corpus": "11111111-1111-1111-1111-111111111111",
        "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
        "parent": "12341234-1234-1234-1234-123412341234",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": None,
    }
    if slim_output:
        assert element_creation_response == "12345678-1234-1234-1234-123456789123"
    else:
        assert Element(element_creation_response) == Element(child_elt)


def test_create_sub_element_confidence(responses, mock_elements_worker):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "corpus": {"id": "11111111-1111-1111-1111-111111111111"},
            "zone": {"image": {"id": "22222222-2222-2222-2222-222222222222"}},
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/create/",
        status=200,
        json={"id": "12345678-1234-1234-1234-123456789123"},
    )

    sub_element_id = mock_elements_worker.create_sub_element(
        element=elt,
        type="something",
        name="0",
        polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        confidence=0.42,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/elements/create/"),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type": "something",
        "name": "0",
        "image": None,
        "corpus": "11111111-1111-1111-1111-111111111111",
        "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
        "parent": "12341234-1234-1234-1234-123412341234",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.42,
    }
    assert sub_element_id == "12345678-1234-1234-1234-123456789123"


def test_create_elements_wrong_parent(mock_elements_worker):
    with pytest.raises(
        TypeError, match="Parent element should be an Element or CachedElement instance"
    ):
        mock_elements_worker.create_elements(
            parent=None,
            elements=[],
        )

    with pytest.raises(
        TypeError, match="Parent element should be an Element or CachedElement instance"
    ):
        mock_elements_worker.create_elements(
            parent="not element type",
            elements=[],
        )


def test_create_elements_no_zone(mock_elements_worker):
    elt = Element({"zone": None})
    with pytest.raises(
        AssertionError, match="create_elements cannot be used on parents without zones"
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=None,
        )

    elt = CachedElement(
        id="11111111-1111-1111-1111-1111111111", name="blah", type="blah"
    )
    with pytest.raises(
        AssertionError, match="create_elements cannot be used on parents without images"
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=None,
        )


def test_create_elements_wrong_elements(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(
        AssertionError, match="elements shouldn't be null and should be of type list"
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=None,
        )

    with pytest.raises(
        AssertionError, match="elements shouldn't be null and should be of type list"
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements="not a list",
        )


def test_create_elements_wrong_elements_instance(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(
        AssertionError, match="Element at index 0 in elements: Should be of type dict"
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=["not a dict"],
        )


def test_create_elements_wrong_elements_name(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: name shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": None,
                    "type": "something",
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: name shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": 1234,
                    "type": "something",
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )


def test_create_elements_wrong_elements_type(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: type shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": None,
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: type shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": 1234,
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )


def test_create_elements_wrong_elements_polygon(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon shouldn't be null and should be of type list",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": None,
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon shouldn't be null and should be of type list",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": "not a polygon",
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon should have at least three points",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1, 1], [2, 2]],
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon points should be lists of two items",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1, 1, 1], [2, 2, 1], [2, 1, 1], [1, 2, 1]],
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon points should be lists of two items",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1], [2], [2], [1]],
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon points should be lists of two numbers",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [["not a coord", 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )


@pytest.mark.parametrize("confidence", ["lol", "0.2", -1.0, 1.42, float("inf")])
def test_create_elements_wrong_elements_confidence(mock_elements_worker, confidence):
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Element at index 0 in elements: confidence should be None or a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_elements(
            parent=Element({"zone": {"image": {"id": "image_id"}}}),
            elements=[
                {
                    "name": "a",
                    "type": "something",
                    "polygon": [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
                    "confidence": confidence,
                }
            ],
        )


def test_create_elements_api_error(responses, mock_elements_worker):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "zone": {
                "image": {
                    "id": "c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
                    "width": 42,
                    "height": 42,
                    "url": "http://aaaa",
                }
            },
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
    ]


def test_create_elements_cached_element(responses, mock_elements_worker_with_cache):
    image = CachedImage.create(
        id=UUID("c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe"),
        width=42,
        height=42,
        url="http://aaaa",
    )
    elt = CachedElement.create(
        id=UUID("12341234-1234-1234-1234-123412341234"),
        type="parent",
        image_id=image.id,
        polygon="[[0, 0], [0, 1000], [1000, 1000], [1000, 0], [0, 0]]",
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=200,
        json=[{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}],
    )

    created_ids = mock_elements_worker_with_cache.create_elements(
        parent=elt,
        elements=[
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
            }
        ],
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "elements": [
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
            }
        ],
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    assert created_ids == [{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}]

    # Check that created elements were properly stored in SQLite cache
    assert list(CachedElement.select().order_by(CachedElement.id)) == [
        elt,
        CachedElement(
            id=UUID("497f6eca-6276-4993-bfeb-53cbbbba6f08"),
            parent_id=elt.id,
            type="something",
            image_id="c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        ),
    ]


def test_create_elements(responses, mock_elements_worker_with_cache, tmp_path):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "zone": {
                "image": {
                    "id": "c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
                    "width": 42,
                    "height": 42,
                    "url": "http://aaaa",
                }
            },
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=200,
        json=[{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}],
    )

    created_ids = mock_elements_worker_with_cache.create_elements(
        parent=elt,
        elements=[
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
            }
        ],
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "elements": [
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
            }
        ],
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    assert created_ids == [{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}]

    # Check that created elements were properly stored in SQLite cache
    assert (tmp_path / "db.sqlite").is_file()

    assert list(CachedElement.select()) == [
        CachedElement(
            id=UUID("497f6eca-6276-4993-bfeb-53cbbbba6f08"),
            parent_id=UUID("12341234-1234-1234-1234-123412341234"),
            type="something",
            image_id="c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
            confidence=None,
        )
    ]


def test_create_elements_confidence(
    responses, mock_elements_worker_with_cache, tmp_path
):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "zone": {
                "image": {
                    "id": "c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
                    "width": 42,
                    "height": 42,
                    "url": "http://aaaa",
                }
            },
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=200,
        json=[{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}],
    )

    created_ids = mock_elements_worker_with_cache.create_elements(
        parent=elt,
        elements=[
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                "confidence": 0.42,
            }
        ],
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "elements": [
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                "confidence": 0.42,
            }
        ],
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    assert created_ids == [{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}]

    # Check that created elements were properly stored in SQLite cache
    assert (tmp_path / "db.sqlite").is_file()

    assert list(CachedElement.select()) == [
        CachedElement(
            id=UUID("497f6eca-6276-4993-bfeb-53cbbbba6f08"),
            parent_id=UUID("12341234-1234-1234-1234-123412341234"),
            type="something",
            image_id="c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
            confidence=0.42,
        )
    ]


def test_create_elements_integrity_error(
    responses, mock_elements_worker_with_cache, caplog
):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "zone": {
                "image": {
                    "id": "c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
                    "width": 42,
                    "height": 42,
                    "url": "http://aaaa",
                }
            },
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=200,
        json=[
            # Duplicate IDs, which will cause an IntegrityError when stored in the cache
            {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
            {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
        ],
    )

    elements = [
        {
            "name": "0",
            "type": "something",
            "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
        },
        {
            "name": "1",
            "type": "something",
            "polygon": [[1, 1], [3, 3], [3, 1], [1, 3]],
        },
    ]

    created_ids = mock_elements_worker_with_cache.create_elements(
        parent=elt,
        elements=elements,
    )

    assert created_ids == [
        {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
        {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
    ]

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message.startswith(
        "Couldn't save created elements in local cache:"
    )

    assert list(CachedElement.select()) == []


@pytest.mark.parametrize(
    ("params", "error_message"),
    [
        (
            {"parent": None, "child": None},
            "parent shouldn't be null and should be of type Element",
        ),
        (
            {"parent": "not an element", "child": None},
            "parent shouldn't be null and should be of type Element",
        ),
        (
            {"parent": Element(zone=None), "child": None},
            "child shouldn't be null and should be of type Element",
        ),
        (
            {"parent": Element(zone=None), "child": "not an element"},
            "child shouldn't be null and should be of type Element",
        ),
    ],
)
def test_create_element_parent_invalid_params(
    mock_elements_worker, params, error_message
):
    with pytest.raises(AssertionError, match=re.escape(error_message)):
        mock_elements_worker.create_element_parent(**params)


def test_create_element_parent_api_error(responses, mock_elements_worker):
    parent = Element({"id": "12341234-1234-1234-1234-123412341234"})
    child = Element({"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/497f6eca-6276-4993-bfeb-53cbbbba6f08/parent/12341234-1234-1234-1234-123412341234/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_element_parent(
            parent=parent,
            child=child,
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        (
            "POST",
            "http://testserver/api/v1/element/497f6eca-6276-4993-bfeb-53cbbbba6f08/parent/12341234-1234-1234-1234-123412341234/",
        ),
    ] * 5


def test_create_element_parent(responses, mock_elements_worker):
    parent = Element({"id": "12341234-1234-1234-1234-123412341234"})
    child = Element({"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/497f6eca-6276-4993-bfeb-53cbbbba6f08/parent/12341234-1234-1234-1234-123412341234/",
        status=200,
        json={
            "parent": "12341234-1234-1234-1234-123412341234",
            "child": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
        },
    )

    created_element_parent = mock_elements_worker.create_element_parent(
        parent=parent,
        child=child,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/497f6eca-6276-4993-bfeb-53cbbbba6f08/parent/12341234-1234-1234-1234-123412341234/",
        ),
    ]
    assert created_element_parent == {
        "parent": "12341234-1234-1234-1234-123412341234",
        "child": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    }


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Element
        (
            {"element": None},
            "element shouldn't be null and should be an Element or CachedElement",
        ),
        (
            {"element": "not element type"},
            "element shouldn't be null and should be an Element or CachedElement",
        ),
    ],
)
def test_partial_update_element_wrong_param_element(
    mock_elements_worker, payload, error
):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Type
        ({"type": 1234}, "type should be a str"),
        ({"type": None}, "type should be a str"),
    ],
)
def test_partial_update_element_wrong_param_type(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Name
        ({"name": 1234}, "name should be a str"),
        ({"name": None}, "name should be a str"),
    ],
)
def test_partial_update_element_wrong_param_name(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Polygon
        ({"polygon": "not a polygon"}, "polygon should be a list"),
        ({"polygon": None}, "polygon should be a list"),
        ({"polygon": [[1, 1], [2, 2]]}, "polygon should have at least three points"),
        (
            {"polygon": [[1, 1, 1], [2, 2, 1], [2, 1, 1], [1, 2, 1]]},
            "polygon points should be lists of two items",
        ),
        (
            {"polygon": [[1], [2], [2], [1]]},
            "polygon points should be lists of two items",
        ),
        (
            {"polygon": [["not a coord", 1], [2, 2], [2, 1], [1, 2]]},
            "polygon points should be lists of two numbers",
        ),
    ],
)
def test_partial_update_element_wrong_param_polygon(
    mock_elements_worker, payload, error
):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Confidence
        ({"confidence": "lol"}, "confidence should be None or a float in [0..1] range"),
        ({"confidence": "0.2"}, "confidence should be None or a float in [0..1] range"),
        ({"confidence": -1.0}, "confidence should be None or a float in [0..1] range"),
        ({"confidence": 1.42}, "confidence should be None or a float in [0..1] range"),
        (
            {"confidence": float("inf")},
            "confidence should be None or a float in [0..1] range",
        ),
    ],
)
def test_partial_update_element_wrong_param_conf(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=re.escape(error)):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Rotation angle
        ({"rotation_angle": "lol"}, "rotation_angle should be a positive integer"),
        ({"rotation_angle": -1}, "rotation_angle should be a positive integer"),
        ({"rotation_angle": 0.5}, "rotation_angle should be a positive integer"),
        ({"rotation_angle": None}, "rotation_angle should be a positive integer"),
    ],
)
def test_partial_update_element_wrong_param_rota(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Mirrored
        ({"mirrored": "lol"}, "mirrored should be a boolean"),
        ({"mirrored": 1234}, "mirrored should be a boolean"),
        ({"mirrored": None}, "mirrored should be a boolean"),
    ],
)
def test_partial_update_element_wrong_param_mir(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Image
        ({"image": "lol"}, "image should be a UUID"),
        ({"image": 1234}, "image should be a UUID"),
        ({"image": None}, "image should be a UUID"),
    ],
)
def test_partial_update_element_wrong_param_image(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


def test_partial_update_element_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.PATCH,
        f"http://testserver/api/v1/element/{elt.id}/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.partial_update_element(
            element=elt,
            type="something",
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        ("PATCH", f"http://testserver/api/v1/element/{elt.id}/"),
        ("PATCH", f"http://testserver/api/v1/element/{elt.id}/"),
        ("PATCH", f"http://testserver/api/v1/element/{elt.id}/"),
        ("PATCH", f"http://testserver/api/v1/element/{elt.id}/"),
        ("PATCH", f"http://testserver/api/v1/element/{elt.id}/"),
    ]


@pytest.mark.usefixtures("_mock_cached_elements", "_mock_cached_images")
@pytest.mark.parametrize(
    "payload",
    [
        (
            {
                "polygon": [[10, 10], [20, 20], [20, 10], [10, 20]],
                "confidence": None,
            }
        ),
        (
            {
                "rotation_angle": 45,
                "mirrored": False,
            }
        ),
        (
            {
                "polygon": [[10, 10], [20, 20], [20, 10], [10, 20]],
                "confidence": None,
                "rotation_angle": 45,
                "mirrored": False,
            }
        ),
    ],
)
def test_partial_update_element(responses, mock_elements_worker_with_cache, payload):
    elt = CachedElement.select().first()
    new_image = CachedImage.select().first()

    elt_response = {
        "image": str(new_image.id),
        **payload,
    }
    responses.add(
        responses.PATCH,
        f"http://testserver/api/v1/element/{elt.id}/",
        status=200,
        # UUID not allowed in JSON
        json=elt_response,
    )

    element_update_response = mock_elements_worker_with_cache.partial_update_element(
        element=elt,
        **{**elt_response, "image": new_image.id},
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "PATCH",
            f"http://testserver/api/v1/element/{elt.id}/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == elt_response
    assert element_update_response == elt_response

    cached_element = CachedElement.get(CachedElement.id == elt.id)
    # Always present in payload
    assert str(cached_element.image_id) == elt_response["image"]
    # Optional params
    if "polygon" in payload:
        # Cast to string as this is the only difference compared to model
        elt_response["polygon"] = str(elt_response["polygon"])

    for param in payload:
        assert getattr(cached_element, param) == elt_response[param]


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize("confidence", [None, 0.42])
def test_partial_update_element_confidence(
    responses, mock_elements_worker_with_cache, confidence
):
    elt = CachedElement.select().first()
    elt_response = {
        "polygon": [[10, 10], [20, 20], [20, 10], [10, 20]],
        "confidence": confidence,
    }
    responses.add(
        responses.PATCH,
        f"http://testserver/api/v1/element/{elt.id}/",
        status=200,
        json=elt_response,
    )

    element_update_response = mock_elements_worker_with_cache.partial_update_element(
        element=elt,
        **elt_response,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "PATCH",
            f"http://testserver/api/v1/element/{elt.id}/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == elt_response
    assert element_update_response == elt_response

    cached_element = CachedElement.get(CachedElement.id == elt.id)
    assert cached_element.polygon == str(elt_response["polygon"])
    assert cached_element.confidence == confidence


def test_list_element_children_wrong_element(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.list_element_children(element=None)

    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.list_element_children(element="not element type")


def test_list_element_children_wrong_folder(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="folder should be of type bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            folder="not bool",
        )


def test_list_element_children_wrong_name(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="name should be of type str"):
        mock_elements_worker.list_element_children(
            element=elt,
            name=1234,
        )


def test_list_element_children_wrong_recursive(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="recursive should be of type bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            recursive="not bool",
        )


def test_list_element_children_wrong_type(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="type should be of type str"):
        mock_elements_worker.list_element_children(
            element=elt,
            type=1234,
        )


def test_list_element_children_wrong_with_classes(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_classes should be of type bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            with_classes="not bool",
        )


def test_list_element_children_wrong_with_corpus(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_corpus should be of type bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            with_corpus="not bool",
        )


def test_list_element_children_wrong_with_has_children(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match="with_has_children should be of type bool"
    ):
        mock_elements_worker.list_element_children(
            element=elt,
            with_has_children="not bool",
        )


def test_list_element_children_wrong_with_zone(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_zone should be of type bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            with_zone="not bool",
        )


def test_list_element_children_wrong_with_metadata(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_metadata should be of type bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            with_metadata="not bool",
        )


@pytest.mark.parametrize(
    ("param", "value"),
    [
        ("worker_run", 1234),
        ("transcription_worker_run", 1234),
    ],
)
def test_list_element_children_wrong_worker_run(mock_elements_worker, param, value):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match=f"{param} should be of type str or bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            **{param: value},
        )


@pytest.mark.parametrize(
    ("param", "alternative", "value"),
    [
        ("worker_version", "worker_run", 1234),
        ("transcription_worker_version", "transcription_worker_run", 1234),
    ],
)
def test_list_element_children_wrong_worker_version(
    mock_elements_worker, param, alternative, value
):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    # WARNING: pytest.deprecated_call must be placed BEFORE pytest.raises, otherwise `match` argument won't be checked
    with (
        pytest.deprecated_call(
            match=f"`{param}` usage is deprecated. Consider using `{alternative}` instead."
        ),
        pytest.raises(AssertionError, match=f"{param} should be of type str or bool"),
    ):
        mock_elements_worker.list_element_children(
            element=elt,
            **{param: value},
        )


@pytest.mark.parametrize(
    "param",
    [
        "worker_run",
        "transcription_worker_run",
    ],
)
def test_list_element_children_wrong_bool_worker_run(mock_elements_worker, param):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match=f"if of type bool, {param} can only be set to False"
    ):
        mock_elements_worker.list_element_children(
            element=elt,
            **{param: True},
        )


@pytest.mark.parametrize(
    ("param", "alternative"),
    [
        ("worker_version", "worker_run"),
        ("transcription_worker_version", "transcription_worker_run"),
    ],
)
def test_list_element_children_wrong_bool_worker_version(
    mock_elements_worker, param, alternative
):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    # WARNING: pytest.deprecated_call must be placed BEFORE pytest.raises, otherwise `match` argument won't be checked
    with (
        pytest.deprecated_call(
            match=f"`{param}` usage is deprecated. Consider using `{alternative}` instead."
        ),
        pytest.raises(
            AssertionError, match=f"if of type bool, {param} can only be set to False"
        ),
    ):
        mock_elements_worker.list_element_children(
            element=elt,
            **{param: True},
        )


def test_list_element_children_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        status=500,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        next(mock_elements_worker.list_element_children(element=elt))

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We do 5 retries
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
    ]


def test_list_element_children(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_children = [
        {
            "id": "0000",
            "type": "page",
            "name": "Test",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        },
        {
            "id": "1111",
            "type": "page",
            "name": "Test 2",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        },
        {
            "id": "2222",
            "type": "page",
            "name": "Test 3",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        },
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": expected_children,
        },
    )

    for idx, child in enumerate(
        mock_elements_worker.list_element_children(element=elt)
    ):
        assert child == expected_children[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
    ]


def test_list_element_children_manual_worker_version(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_children = [
        {
            "id": "0000",
            "type": "page",
            "name": "Test",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        }
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/?worker_version=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": expected_children,
        },
    )

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        for idx, child in enumerate(
            mock_elements_worker.list_element_children(
                element=elt, worker_version=False
            )
        ):
            assert child == expected_children[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/?worker_version=False",
        ),
    ]


def test_list_element_children_manual_worker_run(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_children = [
        {
            "id": "0000",
            "type": "page",
            "name": "Test",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        }
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/?worker_run=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": expected_children,
        },
    )

    for idx, child in enumerate(
        mock_elements_worker.list_element_children(element=elt, worker_run=False)
    ):
        assert child == expected_children[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/?worker_run=False",
        ),
    ]


def test_list_element_children_with_cache_unhandled_param(
    mock_elements_worker_with_cache,
):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError,
        match="When using the local cache, you can only filter by 'type' and/or 'worker_version' and/or 'worker_run'",
    ):
        mock_elements_worker_with_cache.list_element_children(
            element=elt, with_corpus=True
        )


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize(
    ("filters", "expected_ids"),
    [
        # Filter on element should give all elements inserted
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
                "33333333-3333-3333-3333-333333333333",
            ),
        ),
        # Filter on element and page should give the second element
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "type": "page",
            },
            ("22222222-2222-2222-2222-222222222222",),
        ),
        # Filter on element and worker run should give second
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_run": "56785678-5678-5678-5678-567856785678",
            },
            ("22222222-2222-2222-2222-222222222222",),
        ),
        # Filter on element, manual worker run should give first and third
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_run": False,
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "33333333-3333-3333-3333-333333333333",
            ),
        ),
    ],
)
def test_list_element_children_with_cache(
    responses,
    mock_elements_worker_with_cache,
    filters,
    expected_ids,
):
    # Check we have 5 elements already present in database
    assert CachedElement.select().count() == 5

    # Query database through cache
    elements = mock_elements_worker_with_cache.list_element_children(**filters)
    assert elements.count() == len(expected_ids)
    for child, expected_id in zip(elements.order_by("id"), expected_ids, strict=True):
        assert child.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize(
    ("filters", "expected_ids"),
    [
        # Filter on element and worker version
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ),
        ),
        # Filter on element, type double_page and worker version
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "type": "page",
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            ("22222222-2222-2222-2222-222222222222",),
        ),
        # Filter on element, manual worker version
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_version": False,
            },
            ("33333333-3333-3333-3333-333333333333",),
        ),
    ],
)
def test_list_element_children_with_cache_deprecation(
    responses,
    mock_elements_worker_with_cache,
    filters,
    expected_ids,
):
    # Check we have 5 elements already present in database
    assert CachedElement.select().count() == 5

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        # Query database through cache
        elements = mock_elements_worker_with_cache.list_element_children(**filters)
    assert elements.count() == len(expected_ids)
    for child, expected_id in zip(elements.order_by("id"), expected_ids, strict=True):
        assert child.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


def test_list_element_parents_wrong_element(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.list_element_parents(element=None)

    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.list_element_parents(element="not element type")


def test_list_element_parents_wrong_folder(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="folder should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            folder="not bool",
        )


def test_list_element_parents_wrong_name(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="name should be of type str"):
        mock_elements_worker.list_element_parents(
            element=elt,
            name=1234,
        )


def test_list_element_parents_wrong_recursive(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="recursive should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            recursive="not bool",
        )


def test_list_element_parents_wrong_type(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="type should be of type str"):
        mock_elements_worker.list_element_parents(
            element=elt,
            type=1234,
        )


def test_list_element_parents_wrong_with_classes(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_classes should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            with_classes="not bool",
        )


def test_list_element_parents_wrong_with_corpus(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_corpus should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            with_corpus="not bool",
        )


def test_list_element_parents_wrong_with_has_children(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match="with_has_children should be of type bool"
    ):
        mock_elements_worker.list_element_parents(
            element=elt,
            with_has_children="not bool",
        )


def test_list_element_parents_wrong_with_zone(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_zone should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            with_zone="not bool",
        )


def test_list_element_parents_wrong_with_metadata(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_metadata should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            with_metadata="not bool",
        )


@pytest.mark.parametrize(
    ("param", "value"),
    [
        ("worker_run", 1234),
        ("transcription_worker_run", 1234),
    ],
)
def test_list_element_parents_wrong_worker_run(mock_elements_worker, param, value):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match=f"{param} should be of type str or bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            **{param: value},
        )


@pytest.mark.parametrize(
    ("param", "alternative", "value"),
    [
        ("worker_version", "worker_run", 1234),
        ("transcription_worker_version", "transcription_worker_run", 1234),
    ],
)
def test_list_element_parents_wrong_worker_version(
    mock_elements_worker, param, alternative, value
):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    # WARNING: pytest.deprecated_call must be placed BEFORE pytest.raises, otherwise `match` argument won't be checked
    with (
        pytest.deprecated_call(
            match=f"`{param}` usage is deprecated. Consider using `{alternative}` instead."
        ),
        pytest.raises(AssertionError, match=f"{param} should be of type str or bool"),
    ):
        mock_elements_worker.list_element_parents(
            element=elt,
            **{param: value},
        )


@pytest.mark.parametrize(
    "param",
    [
        "worker_run",
        "transcription_worker_run",
    ],
)
def test_list_element_parents_wrong_bool_worker_run(mock_elements_worker, param):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match=f"if of type bool, {param} can only be set to False"
    ):
        mock_elements_worker.list_element_parents(
            element=elt,
            **{param: True},
        )


@pytest.mark.parametrize(
    ("param", "alternative"),
    [
        ("worker_version", "worker_run"),
        ("transcription_worker_version", "transcription_worker_run"),
    ],
)
def test_list_element_parents_wrong_bool_worker_version(
    mock_elements_worker, param, alternative
):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    # WARNING: pytest.deprecated_call must be placed BEFORE pytest.raises, otherwise `match` argument won't be checked
    with (
        pytest.deprecated_call(
            match=f"`{param}` usage is deprecated. Consider using `{alternative}` instead."
        ),
        pytest.raises(
            AssertionError, match=f"if of type bool, {param} can only be set to False"
        ),
    ):
        mock_elements_worker.list_element_parents(
            element=elt,
            **{param: True},
        )


def test_list_element_parents_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        status=500,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        next(mock_elements_worker.list_element_parents(element=elt))

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We do 5 retries
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
    ]


def test_list_element_parents(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_parents = [
        {
            "id": "0000",
            "type": "page",
            "name": "Test",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        },
        {
            "id": "1111",
            "type": "page",
            "name": "Test 2",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        },
        {
            "id": "2222",
            "type": "page",
            "name": "Test 3",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        },
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": expected_parents,
        },
    )

    for idx, parent in enumerate(
        mock_elements_worker.list_element_parents(element=elt)
    ):
        assert parent == expected_parents[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
    ]


def test_list_element_parents_manual_worker_version(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_parents = [
        {
            "id": "0000",
            "type": "page",
            "name": "Test",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        }
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/?worker_version=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": expected_parents,
        },
    )

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        for idx, parent in enumerate(
            mock_elements_worker.list_element_parents(element=elt, worker_version=False)
        ):
            assert parent == expected_parents[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/?worker_version=False",
        ),
    ]


def test_list_element_parents_manual_worker_run(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_parents = [
        {
            "id": "0000",
            "type": "page",
            "name": "Test",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        }
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/?worker_run=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": expected_parents,
        },
    )

    for idx, parent in enumerate(
        mock_elements_worker.list_element_parents(element=elt, worker_run=False)
    ):
        assert parent == expected_parents[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/?worker_run=False",
        ),
    ]


def test_list_element_parents_with_cache_unhandled_param(
    mock_elements_worker_with_cache,
):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError,
        match="When using the local cache, you can only filter by 'type' and/or 'worker_version' and/or 'worker_run'",
    ):
        mock_elements_worker_with_cache.list_element_parents(
            element=elt, with_corpus=True
        )


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize(
    ("filters", "expected_id"),
    [
        # Filter on element
        (
            {
                "element": CachedElement(id="11111111-1111-1111-1111-111111111111"),
            },
            "12341234-1234-1234-1234-123412341234",
        ),
        # Filter on element and double_page
        (
            {
                "element": CachedElement(id="22222222-2222-2222-2222-222222222222"),
                "type": "double_page",
            },
            "12341234-1234-1234-1234-123412341234",
        ),
        # Filter on element and worker run
        (
            {
                "element": CachedElement(id="22222222-2222-2222-2222-222222222222"),
                "worker_run": "56785678-5678-5678-5678-567856785678",
            },
            "12341234-1234-1234-1234-123412341234",
        ),
        # Filter on element, manual worker run
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_run": False,
            },
            "99999999-9999-9999-9999-999999999999",
        ),
    ],
)
def test_list_element_parents_with_cache(
    responses,
    mock_elements_worker_with_cache,
    filters,
    expected_id,
):
    # Check we have 5 elements already present in database
    assert CachedElement.select().count() == 5

    # Query database through cache
    elements = mock_elements_worker_with_cache.list_element_parents(**filters)
    assert elements.count() == 1
    for parent in elements.order_by("id"):
        assert parent.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize(
    ("filters", "expected_id"),
    [
        # Filter on element and worker version
        (
            {
                "element": CachedElement(id="33333333-3333-3333-3333-333333333333"),
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            "12341234-1234-1234-1234-123412341234",
        ),
        # Filter on element, type double_page and worker version
        (
            {
                "element": CachedElement(id="11111111-1111-1111-1111-111111111111"),
                "type": "double_page",
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            "12341234-1234-1234-1234-123412341234",
        ),
        # Filter on element, manual worker version
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_version": False,
            },
            "99999999-9999-9999-9999-999999999999",
        ),
    ],
)
def test_list_element_parents_with_cache_deprecation(
    responses,
    mock_elements_worker_with_cache,
    filters,
    expected_id,
):
    # Check we have 5 elements already present in database
    assert CachedElement.select().count() == 5

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        # Query database through cache
        elements = mock_elements_worker_with_cache.list_element_parents(**filters)
    assert elements.count() == 1
    for parent in elements.order_by("id"):
        assert parent.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS
