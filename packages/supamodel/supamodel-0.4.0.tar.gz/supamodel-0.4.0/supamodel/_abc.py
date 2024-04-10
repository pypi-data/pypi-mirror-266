"""
# Abstract Base Classes

This module contains the abstract base classes for the supamodel package. These classes will help define the core functionality and structure of the models used in the package.

The primary abstract base classes defined in this module are:

* `BaseModel`: An abstract base class for Pydantic models that provides additional functionality and customization options.
* `OrmModel`: An abstract base class for models that interact with databases using an an existing ORM if necessary.
* `Data`: An abstract base class for data models that can handle dynamic fields and aliasing. This class is designed to be flexible and accommodate various data structures between systems.
* `Singleton`: An abstract base class for creating singleton classes that ensure only one instance of the class is created. We work to ensure that the class is thread-safe and can be used in a multi-threaded environment.
* `SupaModel`: An abstract base class for models that interact with Supabase using the Supabase API. This class provides a consistent interface for interacting with Supabase and handling errors.

These abstract base classes provide a foundation for the models used in the supamodel package, ensuring consistency, flexibility, and extensibility across different types of models.


"""

import random
from functools import cached_property
from typing import Any, Dict, Generic, List, Optional, TypeVar, cast

import pandas as pd
from pydantic import (
    AliasGenerator,
    BaseModel as _BaseModel,
    ConfigDict,
    EmailStr,
    alias_generators,
)

from supamodel.utils import cached_classproperty

DataT = TypeVar("DataT", bound="Data")
InputModelT = TypeVar("InputModelT", "BaseModel", "Data")
DataAny = DataT | Any


class BaseModel(_BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        extra="allow",
        populate_by_name=True,
        ignored_types=(cached_property, cached_classproperty),
    )

    def none_dump(self) -> Dict:
        """Return the model's data in a dictionary format without incuding None values.

        Returns:
            Dict: A dict with the model's data without None values.
        """
        return self.model_dump(exclude_none=True)

    def supa_dump(self, by_alias: bool = False) -> Dict:
        """Supabase serialization dump.

        Args:
            by_alias (bool, optional): Option to use aliases. Defaults to False.

        Returns:
            Dict: The response in a dictionary format.
        """
        return self.model_dump(exclude_none=True, mode="json", by_alias=by_alias)


class IgnoreModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class CamelModel(IgnoreModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel)


class OrmModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        ignored_types=(cached_property, cached_classproperty),
        arbitrary_types_allowed=True,
    )


class Data(BaseModel):
    """
    The OpenBB Standardized Data Model.

    The `Data` class is a flexible Pydantic model designed to accommodate various data structures
    for OpenBB's data processing pipeline as it's structured to support dynamic field definitions.

    The model leverages Pydantic's powerful validation features to ensure data integrity while
    providing the flexibility to handle extra fields that are not explicitly defined in the model's
    schema. This makes the `Data` class ideal for working with datasets that may have varying
    structures or come from heterogeneous sources.

    Key Features:
    - Dynamic field support: Can dynamically handle fields that are not pre-defined in the model,
        allowing for great flexibility in dealing with different data shapes.
    - Alias handling: Utilizes an aliasing mechanism to maintain compatibility with different naming
        conventions across various data formats.

    Usage:
    The `Data` class can be instantiated with keyword arguments corresponding to the fields of the
    expected data. It can also parse and validate data from JSON or other serializable formats, and
    convert them to a `Data` instance for easy manipulation and access.

    Example:
        # Direct instantiation
        data_record = Data(name="OpenBB", value=42)

        # Conversion from a dictionary
        data_dict = {"name": "OpenBB", "value": 42}
        data_record = Data(**data_dict)

    The class is highly extensible and can be subclassed to create more specific models tailored to
    particular datasets or domains, while still benefiting from the base functionality provided by the
    `Data` class.

    Attributes:
        __alias_dict__ (Dict[str, str]):
            A dictionary that maps field names to their aliases,
            facilitating the use of different naming conventions.
        model_config (ConfigDict):
            A configuration dictionary that defines the model's behavior,
            such as accepting extra fields, populating by name, and alias
            generation.
    """

    # __alias_dict__: Dict[str, str] = {}

    # def __repr__(self):
    #     """Return a string representation of the object."""
    #     return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in super().model_dump().items()])})"

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        strict=False,
        alias_generator=AliasGenerator(
            validation_alias=alias_generators.to_camel,
            serialization_alias=alias_generators.to_snake,
        ),
    )


class Dataset(OrmModel, Generic[DataT]):
    # model_config = ConfigDict(
    #     from_attributes=True, arbitrary_types_allowed=True, ignored_types=[]
    # )
    # I'm now forcing the data to be a list of DataT
    # This is a breaking change. Luckily it's not used anywhere yet.
    data: Optional[List[DataT]] = []
    message: Optional[str] = None
    error: Optional[str] = None

    @property
    def is_list(self) -> bool:
        return isinstance(self.data, list)

    @property
    def is_dict(self) -> bool:
        return isinstance(self.data, dict)

    @property
    def is_base_model(self) -> bool:
        return isinstance(self.data, BaseModel)

    def sample(self) -> DataT:
        """
        Selects and returns a random item from the data.

        If the data is a list, a random item from the list is returned.
        If the data is a dictionary, a random item from the dictionary values is returned.
        If the data is neither a list nor a dictionary, the data itself is returned.

        Returns:
            Any: A random item from the data.
        """
        if self.is_list:
            return random.choice(self.data)
        return self.data

    # Add iterator methods if the data is a list
    def __iter__(self):
        if self.is_list:
            return iter(self.data)
        return iter([])

    def __getitem__(self, item):
        if self.is_list or self.is_dict:
            return self.data[item]
        return None

    def __len__(self):
        if self.is_list:
            return len(self.data)
        return 0

    def __contains__(self, item):
        if self.is_list:
            return item in self.data
        return False

    def empty(self) -> bool:
        if self.is_list:
            return len(self.data) == 0
        return True

    def to_dict(self) -> Dict[str, DataT] | List[DataT | Any] | Any:
        if self.is_list:
            self.data = cast(List[DataT], self.data)
            return [item.model_dump(by_alias=True) for item in self.data]
        elif self.is_dict:
            return self.data
        elif self.is_base_model:
            return self.data.model_dump(by_alias=True)
        return self.data

    def to_df(self) -> Any:
        if self.empty():
            return pd.DataFrame([])

        dataset_list = self.to_dict()
        if not isinstance(dataset_list, list):
            dataset_list = [dataset_list]
        return pd.DataFrame(dataset_list)


# -----------------------------------------------------------
# Local Testing
# -----------------------------------------------------------


class User(Data):
    username: str
    email: EmailStr
    age: int


def main():
    pass


if __name__ == "__main__":
    main()
