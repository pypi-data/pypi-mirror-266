# datasette-updated

[![PyPI](https://img.shields.io/pypi/v/datasette-updated.svg)](https://pypi.org/project/datasette-updated/)
[![Changelog](https://img.shields.io/github/v/release/rcaught/datasette-updated?include_prereleases&label=changelog)](https://github.com/rcaught/datasette-updated/releases)
[![Tests](https://github.com/rcaught/datasette-updated/workflows/Test/badge.svg)](https://github.com/rcaught/datasette-updated/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/rcaught/datasette-updated/blob/main/LICENSE)

Display the date your data was updated

## Installation

Install this plugin in the same environment as Datasette.
```bash
datasette install datasette-updated
```
## Usage
You can have a different `updated` value per table, database or Datasette instance. If undefined at any level, `updated` will fall back in that order. If no value is set, `updated` will be `unknown`.

### Base metadata configuration
If you have known `updated` values, you can define them in your base `metadata.(json|yml)`:
```json
{
  "plugins": {
    "datasette-updated": {
      "updated": "2023-12-14T23:04:42+00:00"
    }
  },
  "databases": {
    "my-database-name": {
      "plugins": {
        "datasette-updated": {
          "updated": "2023-01-01T00:00:00+00:00"
        }
      },
      "tables": {
        "my-table-name": {
          "plugins": {
            "datasette-updated": {
              "updated": "2020-01-01T00:00:00+00:00"
            }
          }
          ...
```

### Plugin metadata configuration
If you want to define more dynamic `updated` value(s) on `datasette package` or `datasette publish`, put metadata for this plugin in `YOUR_PLUGINS_DIR/datasette-updated/metadata.(json|yml)`. The following is an example that sets `updated` to the current date/time.
```sh
mkdir -p plugins/datasette-updated/ && \
echo '{
  "plugins": {
    "datasette-updated": {
      "updated": "'"$(date -Iseconds)"'"
    }
  }
}' > plugins/datasette-updated/metadata.json && \
datasette publish --plugins-dir=plugins --install=datasette-updated ...
```

### Combined metadata configuration
You can combine base metadata and plugin metadata configuration, but be aware that the base `metadata.(json|yml)` will always win if there is a duplicate configuration value.

### Extra configuration
The base / instance level metadata can accept the following extra configuration (that will apply to all levels):
- `time_type` (default: `time-ago`)

  - `time`: [2023-12-01T00:00:00+00:00](https://github.com/basecamp/local_time/tree/main#time-and-date-helpers)
  - `date`: ["Apr 11" or "Apr 11, 2013"](https://github.com/basecamp/local_time/tree/main#relative-time-helpers)
  - `time-ago`: ["a second ago", "32 seconds ago", "an hour ago", "14 hours ago"](https://github.com/basecamp/local_time/tree/main#time-ago-helpers)
  - `time-or-date`: ["3:26pm" or "Apr 11"](https://github.com/basecamp/local_time/tree/main#relative-time-helpers)
  - `weekday`: ["Today", "Yesterday", or the weekday](https://github.com/basecamp/local_time/tree/main#relative-time-helpers)
  - `weekday-or-date`: ["Yesterday" or "Apr 11"](https://github.com/basecamp/local_time/tree/main#relative-time-helpers)


  ```json
  {
    "plugins": {
      "datasette-updated": {
        "time_type": "time"
      }
    }
  }
  ```

### Display
The plugin will try to load a footer template that is copied from the default Datasette footer template, but with the following addition:

```html
{% if datasette_updated %}&middot;
    Updated:
    <time
      data-local="{{ datasette_updated.time_type }}"
      datetime="{{ datasette_updated.updated }}">
        {{ datasette_updated.updated }}
    </time>
{% endif %}
```

- **If you have your own custom footer template, you will need to add the above code**, as your base template will take precedence.
- Look at [local_time](https://github.com/basecamp/local_time/tree/main#example) for extra configuration options (just ignore the Ruby parts).

## Screenshot and Demo
![screenshot](https://github.com/rcaught/datasette-updated/raw/master/screenshot.png)
- Example site: https://querydata.io/
- The Javascript component converts time elements from UTC to the browser's local time.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd datasette-updated
python3 -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
pytest
```
