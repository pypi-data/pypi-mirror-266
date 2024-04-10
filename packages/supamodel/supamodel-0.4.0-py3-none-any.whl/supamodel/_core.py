from typing import Dict, TypeVar

# from copier import ConfigDict
from pydantic import (
    AliasGenerator,
    BaseModel as _BaseModel,
    ConfigDict,
    alias_generators,
)

DataT = TypeVar("DataT", bound="Data")
InputModelT = TypeVar("InputModelT", "BaseModel", "Data")


class BaseModel(_BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        extra="allow",
        populate_by_name=True,
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
