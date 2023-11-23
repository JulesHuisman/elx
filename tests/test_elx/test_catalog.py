import pytest
from elx import Tap
from elx.catalog import Catalog, Stream

DEFAULT_CATALOG = {
    "streams": [
        {
            "tap_stream_id": "animals",
            "replication_method": "FULL_TABLE",
            "key_properties": ["id"],
            "replication_key": None,
            "is_view": False,
            "table_name": None,
            "schema": {
                "properties": {
                    "id": {"type": ["integer", "null"]},
                    "animal_name": {"type": ["string", "null"]},
                    "updated_at": {"format": "date-time", "type": ["string", "null"]},
                },
                "type": "object",
            },
            "metadata": [
                {
                    "breadcrumb": ["properties", "id"],
                    "metadata": {"inclusion": "automatic"},
                },
                {
                    "breadcrumb": ["properties", "animal_name"],
                    "metadata": {"inclusion": "available"},
                },
                {
                    "breadcrumb": ["properties", "updated_at"],
                    "metadata": {"inclusion": "available"},
                },
                {
                    "breadcrumb": [],
                    "metadata": {
                        "inclusion": "available",
                        "selected": False,
                        "selected-by-default": False,
                        "table-key-properties": ["id"],
                    },
                },
            ],
        },
        {
            "tap_stream_id": "users",
            "replication_key": "updated_at",
            "replication_method": "INCREMENTAL",
            "is_view": False,
            "table_name": None,
            "key_properties": ["id"],
            "schema": {
                "properties": {
                    "id": {"type": ["integer", "null"]},
                    "name": {"type": ["string", "null"]},
                    "updated_at": {"format": "date-time", "type": ["string", "null"]},
                },
                "type": "object",
            },
            "metadata": [
                {
                    "breadcrumb": ["properties", "id"],
                    "metadata": {"inclusion": "automatic"},
                },
                {
                    "breadcrumb": ["properties", "name"],
                    "metadata": {"inclusion": "available"},
                },
                {
                    "breadcrumb": ["properties", "updated_at"],
                    "metadata": {"inclusion": "automatic"},
                },
                {
                    "breadcrumb": [],
                    "metadata": {
                        "inclusion": "available",
                        "selected": True,
                        "selected-by-default": True,
                        "table-key-properties": ["id"],
                        "valid-replication-keys": ["updated_at"],
                    },
                },
            ],
        },
    ]
}


def test_catalog(tap: Tap):
    """
    Make sure that the catalog selector returns the same catalog if no streams are selected.
    """
    assert tap.catalog.dict(by_alias=True) == DEFAULT_CATALOG


def test_catalog_select(tap: Tap):
    """If we select a stream, the catalog should be updated."""
    catalog = tap.catalog.select(["animals"])

    assert catalog.streams[0].is_selected == True

    catalog = tap.catalog.select([])

    assert catalog.streams[0].is_selected == False


def test_catalog_no_deselect(tap: Tap):
    """If we don't deselect anything, the catalog should be the same."""
    catalog = tap.catalog.deselect()
    assert catalog == tap.catalog


def test_catalog_deselect_stream(tap: Tap):
    """If we deselect a stream, the catalog should be updated."""
    catalog = tap.catalog.deselect(["users"])

    assert catalog.streams[1].is_selected == False


def test_catalog_deselect_invalid_stream(tap: Tap):
    """If we try to deselect an invalid stream, the catalog should be the same."""
    catalog = tap.catalog.deselect(["invalid"])
    assert catalog == tap.catalog


def test_catalog_deselect_property(tap: Tap):
    """If we deselect a property, the catalog should be updated."""
    catalog = tap.catalog.deselect(["animals.id"])
    catalog_dict = catalog.dict(by_alias=True)

    assert catalog_dict["streams"][0]["metadata"][0]["metadata"]["selected"] == False


def test_catalog_replication_method(tap: Tap):
    """If we have an incremental stream, the replication_method in the catalog should be `INCREMENTAL`."""
    catalog_dict = tap.catalog.dict(by_alias=True)

    assert (
        catalog_dict["streams"][1]["replication_method"]
        == DEFAULT_CATALOG["streams"][1]["replication_method"]
    )


def test_catalog_replication_key(tap: Tap):
    """If we have an incremental stream, the catalog should have a `replication_key`."""
    catalog_dict = tap.catalog.dict(by_alias=True)

    assert catalog_dict["streams"][1]["replication_key"] != None

    assert (
        catalog_dict["streams"][1]["replication_key"]
        == DEFAULT_CATALOG["streams"][1]["replication_key"]
    )


def test_catalog_valid_replication_keys(tap: Tap):
    """
    If we have an incremental stream, the catalog should have a metadata breadcrumb for the incremental
    stream containing the key: `valid-replication-keys`.

    This key should be associated with a list containing the fields that could be used as replication keys.
    For example, the metadata breadcrumb of the stream should look as follows if `updated_at` is its replication_key.

    "metadata": {
        "inclusion": "available",
        "selected": True,
        "selected-by-default": True,
        "table-key-properties": ["id"],
        "valid-replication-keys": ["updated_at"],
    }
    """
    catalog_dict = tap.catalog.dict(by_alias=True)

    replication_keys = catalog_dict["streams"][1]["metadata"][-1]["metadata"].get(
        "valid-replication-keys", None
    )

    # Checks that value of `valid-replication-keys` equals to the replication-key
    assert replication_keys == [DEFAULT_CATALOG["streams"][1]["replication_key"]]


def test_catalog_set_stream_replication_key(tap: Tap):
    """If we define a replication key, the catalog should be updated."""
    catalog = tap.catalog

    assert catalog.streams[1].replication_method == "INCREMENTAL"
    assert catalog.streams[1].replication_key == "updated_at"
