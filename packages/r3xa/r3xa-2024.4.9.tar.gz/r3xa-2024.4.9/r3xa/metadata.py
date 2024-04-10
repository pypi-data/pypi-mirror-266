# -*- coding: utf-8 -*-
import slugify
import json

from r3xa.utils import get_schema, random_slug, obj, obj_iter, slugify_file_name, highlight_json
from r3xa.validation import validate

#####################
# Meta data classes #
#####################


class Unit:
    """Independant class that handles units to produces json objects formated as:
    ```json
    {
        "unit": {"type": "string"},
        "value": {"type": "float"},
        "scale": {"type": "float"}
    }
    ```
    """

    def __init__(self, unit: str, value: float = None, scale: float = None):
        self.unit = unit
        self.value = value
        self.scale = scale

    def __str__(self):
        return highlight_json(self)

    def __iter__(self):
        for k, v in obj_iter(self):
            yield k, v


class DataSetFile:
    """Independant class that handles data set file (either `timestamps` or `data`) to produces json objects formated as:
    ```json
    {
        "filename": {"type": "string"},
        "delimiter": {"type": "string", "enum": [":", ",", ...]},
        "data_range": {"type": "array", "items": {"type": "string"}}
    }
    ```
    """

    def __init__(self, filename: str, data_range: list, delimiter: str = ";"):
        self.filename = filename
        self.data_range = data_range
        self.delimiter = delimiter

    def __iter__(self):
        for k, v in obj_iter(self):
            yield k, v

    def __str__(self):
        return highlight_json(self)


class Data:
    """Generic parent class for `data_sets`, `data_sources` and `settings`.
    It can take any `key: values` arguments to keep flexible in view of specs changes.
    Therefore it is agnostic to the specifications implemented in the scheme.

    It implements the `__iter__` function to ease the conversion to json objects.
    """

    def __init__(self, **kwargs):
        # get all attributes from the kwargs and set them
        for k, v in kwargs.items():
            # if obj(v):
            #     setattr(self, k, v)
            setattr(self, k, v)

        # define an ID of the data as the slugified title appended with and random slug
        if not hasattr(self, "id"):
            if hasattr(self, "title"):
                self.id = slugify.slugify(self.title) + "_" + random_slug()
            else:
                self.id = "no_title_" + random_slug()

    def __str__(self):
        return highlight_json(self)

    def __iter__(self):
        for k, v in obj_iter(self):
            yield k, v

    def check_keywords(self, data_type):
        """Raise ValueError if the attributes of the instance does not match
        any required keys of each objects of data_type.

        data_type can be "setting", "data_source" or "data_set"

        Warning:
        --------
            Does not check the data type
        """
        # check that all required data from the specs are present
        # check for data_sets, data_sources and settings
        schema = get_schema()

        # get all keys
        keys = set(self.__dict__.keys())

        missing_keys = []

        # compare keys given to keys required
        # for each object of data_type (e.g, generic, camera, tomograph, for data_type=data_source)
        for k, v in schema["$defs"][data_type].items():
            # get required keys from the specs
            required = set(v["required"])

            # compute missing keys for this specific object and
            # append to global missing keys dictionnary
            missing_keys.append(required.difference(keys))

        # compute intersection between all missing keys sets
        # should be len(0) of one good match
        missing = set.intersection(*missing_keys)

        if len(missing):
            raise ValueError(f"Missing at least the following keys: {missing}")


class Setting(Data):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if len(kwargs):  # skip check if no kwargs entered
            self.check_keywords("setting")

    def load_json(self, payload):
        for k, v in payload.items():
            setattr(self, k, obj(v))


class DataSource(Data):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if len(kwargs):  # skip check if no kwargs entered
            self.check_keywords("data_source")

    def add_data_set(self, data_set: Data):
        self.input_data_set = data_set.id


class DataSet(Data):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if len(kwargs):  # skip check if no kwargs entered
            self.check_keywords("data_set")

    def add_data_source(self, data_source: Data):
        if not hasattr(self, "data_sources"):
            self.data_sources = []
        self.data_sources.append(data_source.id)
        # self.data_sources = datasource.id


class MetaData:
    def __init__(self, **kargs):
        schema = get_schema()
        for k, v in kargs.items():
            if obj(v):
                setattr(self, k, v)

        # add by default settings / data_sources and data_sets
        for k in ["settings", "data_sources", "data_sets"]:
            if not hasattr(self, k):
                setattr(self, k, [])

            # sanity check to remove duplicated ID
            data = {d.id: d for d in getattr(self, k)}
            setattr(self, k, list(data.values()))

        # enforce version from schema
        self.version = schema["properties"]["version"]["const"]

    def __iter__(self):
        for k, v in obj_iter(self):
            yield k, v

    def __str__(self):
        return highlight_json(self)

    def validate(self):
        validate(dict(self))

    def create_or_modify(self, what, where):
        """Insure that when we had Data we don't duplicate the same ID."""
        # get existing data and use id as a key
        data = {d.id: d for d in getattr(self, where)}

        # add current data to existing (by the key)
        data[what.id] = what

        # convert dict to list of data
        setattr(self, where, list(data.values()))

    def add_setting(self, setting: Setting):
        self.create_or_modify(setting, "settings")

    def add_data_source(self, data_source: DataSource):
        self.create_or_modify(data_source, "data_sources")

    def add_data_set(self, data_set: DataSet):
        self.create_or_modify(data_set, "data_sets")

    def load(self, payload):
        """Fill class attributes based on a payload"""
        # Global
        for k, v in payload.items():
            if k in ["settings", "data_sources", "data_sets"]:
                continue
            if not obj(v):
                continue
            setattr(self, k, obj(v))

        # Settings
        for p in payload.get("settings", []):
            s = Setting()
            s.load_json(p)
            self.add_setting(s)

        # Data Source

        # Data Sets

    def save_json(self, name: str = None, check: bool = True):
        """Appends .json to name"""
        # check validity
        if check:
            validate(dict(self))

        # slugify the json file name
        # if not set use the title
        if name:
            name = slugify_file_name(name)
        else:
            name = slugify.slugify(self.title)

        # write file
        json.dump(dict(self), open(name + ".json", "w"), indent=4)
