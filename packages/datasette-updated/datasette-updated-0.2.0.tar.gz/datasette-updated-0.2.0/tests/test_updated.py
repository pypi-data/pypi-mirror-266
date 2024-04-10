from datasette.app import Datasette
import sqlite_utils
import pytest


@pytest.mark.asyncio
async def test_plugin_is_installed():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/-/plugins.json")
    assert response.status_code == 200
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-updated" in installed_plugins


@pytest.fixture
def db_and_path(tmpdir):
    path = str(tmpdir / "data.db")
    db = sqlite_utils.Database(path)
    db.table("cities").insert_all(
        [
            {
                "id": "nyc",
                "name": "New York City",
            },
            {
                "id": "london",
                "name": "London",
            },
            {
                "id": "sf",
                "name": "San Francisco",
            },
        ],
        pk="id",
    )
    return db, path


@pytest.fixture
def db_path(db_and_path):
    return db_and_path[1]


@pytest.fixture
def db(db_and_path):
    return db_and_path[0]


@pytest.mark.asyncio
async def test_plugin_no_config():
    datasette = Datasette(memory=True)
    assert datasette.metadata() == {
        "plugins": {
            "datasette-updated": {"time_type": "time-ago", "updated": "unknown"}
        }
    }

    response = await datasette.client.get(datasette.urls.instance())
    assert (
        """
    &middot;
        Updated:
        <time
          data-local="time-ago"
          datetime="unknown">
            unknown
        </time>
"""
        in response.text
    )


@pytest.mark.asyncio
async def test_plugin_static_no_fallback_config(db_path):
    datasette = Datasette(
        [db_path],
        metadata={
            "plugins": {"datasette-updated": {"updated": "2023-01-01T00:00:00+00:00"}},
            "databases": {
                "data": {
                    "plugins": {
                        "datasette-updated": {"updated": "2000-01-01T00:00:00+00:00"}
                    },
                    "tables": {
                        "cities": {
                            "plugins": {
                                "datasette-updated": {
                                    "updated": "1900-01-01T00:00:00+00:00"
                                }
                            }
                        }
                    },
                }
            },
        },
    )

    response = await datasette.client.get(datasette.urls.instance())
    assert (
        """
    &middot;
        Updated:
        <time
          data-local="time-ago"
          datetime="2023-01-01T00:00:00+00:00">
            2023-01-01T00:00:00+00:00
        </time>
"""
        in response.text
    )

    response = await datasette.client.get(datasette.urls.database("data"))
    assert (
        """
    &middot;
        Updated:
        <time
          data-local="time-ago"
          datetime="2000-01-01T00:00:00+00:00">
            2000-01-01T00:00:00+00:00
        </time>
"""
        in response.text
    )

    response = await datasette.client.get(datasette.urls.table("data", "cities"))
    assert (
        """
    &middot;
        Updated:
        <time
          data-local="time-ago"
          datetime="1900-01-01T00:00:00+00:00">
            1900-01-01T00:00:00+00:00
        </time>
"""
        in response.text
    )


@pytest.mark.asyncio
async def test_plugin_static_fallback_config(db_path):
    datasette = Datasette(
        [db_path],
        metadata={
            "plugins": {"datasette-updated": {"updated": "2023-01-01T00:00:00+00:00"}},
            "databases": {
                "data": {
                    "tables": {"cities": {}},
                }
            },
        },
    )

    response = await datasette.client.get(datasette.urls.instance())
    assert (
        """
    &middot;
        Updated:
        <time
          data-local="time-ago"
          datetime="2023-01-01T00:00:00+00:00">
            2023-01-01T00:00:00+00:00
        </time>
"""
        in response.text
    )

    response = await datasette.client.get(datasette.urls.database("data"))
    assert (
        """
    &middot;
        Updated:
        <time
          data-local="time-ago"
          datetime="2023-01-01T00:00:00+00:00">
            2023-01-01T00:00:00+00:00
        </time>
"""
        in response.text
    )

    response = await datasette.client.get(datasette.urls.table("data", "cities"))
    assert (
        """
    &middot;
        Updated:
        <time
          data-local="time-ago"
          datetime="2023-01-01T00:00:00+00:00">
            2023-01-01T00:00:00+00:00
        </time>
"""
        in response.text
    )


@pytest.mark.asyncio
async def test_plugin_dynamic_config(db_path):
    datasette = Datasette([db_path], plugins_dir="tests/plugins")

    assert datasette.metadata() == {
        "plugins": {
            "datasette-updated": {
                "time_type": "time-ago",
                "updated": "2023-12-01T00:00:00+00:00",
            }
        }
    }

    response = await datasette.client.get(datasette.urls.instance())
    assert (
        """
    &middot;
        Updated:
        <time
          data-local="time-ago"
          datetime="2023-12-01T00:00:00+00:00">
            2023-12-01T00:00:00+00:00
        </time>
"""
        in response.text
    )


@pytest.mark.asyncio
async def test_plugin_time_type_config(db_path):
    datasette = Datasette([db_path], metadata={"plugins": {"datasette-updated": {}}})

    assert datasette.metadata() == {
        "plugins": {
            "datasette-updated": {
                "time_type": "time-ago",
                "updated": "unknown",
            }
        }
    }

    response = await datasette.client.get(datasette.urls.instance())
    assert (
        """
    &middot;
        Updated:
        <time
          data-local="time-ago"
          datetime="unknown">
            unknown
        </time>
"""
        in response.text
    )

    datasette = Datasette(
        [db_path], metadata={"plugins": {"datasette-updated": {"time_type": "time"}}}
    )

    assert datasette.metadata() == {
        "plugins": {
            "datasette-updated": {
                "time_type": "time",
                "updated": "unknown",
            }
        }
    }

    response = await datasette.client.get(datasette.urls.instance())
    assert (
        """
    &middot;
        Updated:
        <time
          data-local="time"
          datetime="unknown">
            unknown
        </time>
"""
        in response.text
    )
