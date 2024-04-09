# -*- coding: utf-8 -*-
import slugify
import json

from r3xa.utils import get_schema, random_slug, obj
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

    Note:
    -----
       `scale` is not returned if None
       `value` is returned as null if None
    """

    def __init__(self, unit: str, value: float = None, scale: float = None):
        self.unit = unit
        self.value = value
        self.scale = scale

    def __iter__(self):
        yield "unit", self.unit
        yield "value", self.value
        # return scale only if defined
        if self.scale:
            yield "scale", self.scale

    def __str__(self):
        if self.value and self.scale:
            return f"{self.value} {self.unit} (x{self.scale:.1e} to SI)"
        elif self.value:
            return f"{self.value} {self.unit}"
        else:
            return self.unit


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
        for k, v in self.__dict__.items():
            yield k, v

    def __str__(self):
        return f"{self.filename} from {self.data_range[0]} to {self.data_range[1]}"


class Data:
    """Generic parent class for `data_sets`, `data_sources` and `settings`.
    It can take any `key: values` arguments to keep flexible in view of specs changes.
    Therefore it is agnostic to the specifications implemented in the scheme.

    It implements the `__iter__` function to ease the conversion to json objects.
    """

    def __init__(self, title="My Data", **kwargs):
        # force title default to be sure to build an id
        self.title = title

        # get all attributes from the kwargs and set them
        for k, v in kwargs.items():
            setattr(self, k, v)

        # define an ID of the data as the slugified title appended with and random slug
        self.id = slugify.slugify(self.title) + "_" + random_slug()

        print(f"Init {self}")

    def __str__(self):
        return f"{self.title} [{self.id}]"

    def __iter__(self):
        """Defines the conversion between instance and dictionnary
        It does ouput unset values and convert list of Iterable to dict if possible.
        """
        for k, v in self.__dict__.items():
            # ignore unset values
            if not v:
                continue

            # convert list of Iterable to list of dict if possible
            # used for our own classes where __iter__ is defined
            if isinstance(v, list):
                v = [obj(_) for _ in v]

            # yield the key: value pair
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
    def __init__(self, title="My setting", **kwargs):
        super().__init__(title=title, **kwargs)
        self.check_keywords("setting")

    def __str__(self):
        return f"Setting: {self.title} [{self.id}]"


class DataSource(Data):
    def __init__(self, title="My data source", **kwargs):
        super().__init__(title=title, **kwargs)
        self.check_keywords("data_source")

    def __str__(self):
        return f"Data source: {self.title} [{self.id}]"

    def add_data_set(self, data_set: Data):
        self.input_data_set = data_set.id


class DataSet(Data):
    def __init__(self, title="My data set", **kwargs):
        super().__init__(title=title, **kwargs)
        self.check_keywords("data_set")

    def __str__(self):
        return f"Data set: {self.title} [{self.id}]"

    def add_data_source(self, data_source: Data):
        if not hasattr(self, "data_sources"):
            self.data_sources = []
        self.data_sources.append(data_source.id)
        # self.data_sources = datasource.id


class MetaData:
    def __init__(self, **kargs):
        schema = get_schema()
        for k, v in kargs.items():
            setattr(self, k, v)

        # enforce version from schema
        self.version = schema["properties"]["version"]["const"]

    def add_setting(self, setting: Setting):
        if not hasattr(self, "settings"):
            self.settings = []
        self.settings.append(setting)

    def add_data_source(self, data_source: DataSource):
        if not hasattr(self, "data_sources"):
            self.data_sources = []
        self.data_sources.append(data_source)

    def add_data_set(self, data_set: DataSet):
        if not hasattr(self, "data_sets"):
            self.data_sets = []
        self.data_sets.append(data_set)

    def create_json(self, name: str = None, check: bool = True):
        # init metadata dictionary
        metadata = {}

        # slugify the json file name
        # if not set use the title
        name = slugify.slugify(name if name else self.title)

        # build dictionnary
        for k, v in self.__dict__.items():
            # ignore specific keywords
            # if k in []:
            #     continue

            # convert iterable to sereliazable objects
            metadata[k] = obj(v)

        # write file
        json.dump(metadata, open(f"{name}.json", "w"), indent=4)

        # check validity
        if check:
            validate(metadata)
