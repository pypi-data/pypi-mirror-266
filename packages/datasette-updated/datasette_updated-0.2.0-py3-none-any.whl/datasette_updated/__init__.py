import os
from datasette import hookimpl
from datasette.utils import parse_metadata
from deepmerge import always_merger


@hookimpl
def get_metadata(datasette, key, database, table):
    try:
        datasette.plugins_dir = datasette.plugins_dir or "plugins"

        candidates = []
        for file in os.listdir(f"{datasette.plugins_dir}/datasette-updated/"):
            for extension in (".json", ".yaml", ".yml"):
                if file.startswith("metadata.") and file.endswith(extension):
                    candidates.append(
                        f"{datasette.plugins_dir}/datasette-updated/{file}"
                    )

        if len(candidates) != 0:
            updated_file = open(
                candidates[0],
                "r",
                encoding="utf8",
            )

            with updated_file:
                metadata = always_merger.merge(
                    metadata_defaults(), parse_metadata(updated_file.read())
                )

                assert metadata["plugins"]["datasette-updated"]["time_type"] in [
                    "time",
                    "date",
                    "time-ago",
                    "time-or-date",
                    "weekday",
                    "weekday-or-date",
                ]

                return metadata
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        return metadata_defaults()


def metadata_defaults():
    return {
        "plugins": {
            "datasette-updated": {"time_type": "time-ago", "updated": "unknown"}
        }
    }


@hookimpl
def extra_template_vars(datasette, database, table):
    base_config = datasette.plugin_config("datasette-updated")
    specific_config = datasette.plugin_config(
        "datasette-updated", database=database, table=table
    )

    return {"datasette_updated": always_merger.merge(base_config, specific_config)}


@hookimpl
def extra_js_urls():
    return [
        {
            "url": "https://cdn.jsdelivr.net/npm/local-time@3.0.2/app/assets/javascripts/local-time.es2017-umd.js",
            "sri": "sha384-l4PZDWQdg3uX/iY4bmkakiAYpcvOOarVJY77JwQ7edY2+c2IdUro71pKH2029xvq",
        }
    ]


@hookimpl
def extra_body_script():
    return {
        "script": "LocalTime.start()",
    }
