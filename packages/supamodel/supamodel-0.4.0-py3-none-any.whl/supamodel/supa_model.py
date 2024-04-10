# """Get it SupaModel, because it's like a SuperModel, but Supa!"""

# import contextlib
# import uuid
# from functools import cached_property
# from typing import Any, Optional, Type, TypeVar

# from loguru import logger
# from postgrest._sync.request_builder import SyncQueryRequestBuilder
# from pydantic import ConfigDict, field_serializer, model_validator

# # from pydantic.dataclasses import dataclass
# from rich import print

# from galapy.app.utils.formatting import tableize
# from galapy.config import supa_client as supabase
# from galapy.models.abstracts.data import Data
# from galapy.models.abstracts.dataset import Dataset
# from galapy.utils.decorators import cached_classproperty
# from galapy.utils.fn_tools import in_all_dicts, serialize_dict

# # from galapy.models.supas.core import Exchange

# SupaModelT = TypeVar("SupaModelT", bound=Data)
# ReqBuilderT = TypeVar("ReqBuilderT", bound=SyncQueryRequestBuilder)
# # PartT = TypeVar("PartT")
# SupaItem = TypeVar("SupaItem")


# class ResponseModel(Data):
#     model_config = ConfigDict(from_attributes=True)
#     data: list[dict[str, Any]] | None = []
#     count: int | None = None
#     error: str | None = None

#     def is_error(self):
#         return self.error is not None

#     def is_success(self) -> bool:
#         return self.error is None and self.data is not None

#     def empty(self) -> bool:
#         return self.data is None or len(self.data) == 0


# class SupaModel(Data):

#     id: uuid.UUID | None = None

#     # Like Super Model, but Supa
#     @field_serializer("id")
#     def serialize_courses_in_order(exchange_id: uuid.UUID | None):
#         if exchange_id is None:
#             return None
#         return str(exchange_id)

#     @classmethod
#     def table_name(cls) -> str:
#         return tableize(cls.__name__)

#     @cached_classproperty
#     def table(cls) -> SyncQueryRequestBuilder:
#         return supabase.table(cls.table_name())

#     @cached_classproperty
#     def class_type(cls):
#         """
#         Returns the class type of an instance created from the model. It must be an instance so tha we don't get the parent class type.
#         It would get ModelMetaClass instead of the current model normally instead.
#         """
#         instance = cls.model_construct({})
#         return type(instance)

#     @cached_classproperty
#     def dataset(cls):
#         """
#         Returns the dataset associated with the class.
#         """
#         return Dataset[cls.class_type]

#     @classmethod
#     def sync_by_id(cls, id: str) -> SupaModelT:
#         return cls.find_one(query_params={"id": id})

#     @classmethod
#     def rpc(cls, method: str, data: dict[str, Any]) -> ReqBuilderT:
#         query: ReqBuilderT = supabase.rpc(method, params=data)
#         # self.execute_dataset(query)
#         return query
#         # return self.execute_dataset(query)

#     @classmethod
#     def select(cls, columns: list[str] = ["*"]) -> ReqBuilderT:
#         return cls.table.select(*columns)

#     @classmethod
#     def select_eq(
#         cls, columns: list[str] = ["*"], inputs: dict[str, Any] = {}
#     ) -> ReqBuilderT:
#         # Looks for exact matches in the table
#         builder = cls.select(columns)
#         if not inputs:
#             return builder
#         for key, value in inputs.items():
#             builder = builder.eq(key, value)
#         return builder

#     @classmethod
#     def extract(
#         cls, query: ReqBuilderT, type_var: Optional[Type[SupaModelT]] = None
#     ) -> Dataset[SupaModelT]:
#         # Since most supabase queries return an object with a data attribute, and count attribute, this method will parse that information and the containing model's data attribute (subclasses of SupaModel).
#         response = query.execute()
#         response = ResponseModel.model_validate(response)
#         if response.is_error():
#             raise Exception(response.error)
#         resp_data = response.data
#         if type_var is not None:
#             return Dataset[type_var](data=resp_data)
#         return cls.dataset(data=resp_data)

#     def sync(self) -> SupaModelT:
#         dump = self.model_dump(exclude_none=True, round_trip=True)
#         found = self.find_one(query_params=dump)

#         if found is None:
#             return None
#         # for key, value in found:
#         #     print((key, value))
#         for key, value in found:
#             with contextlib.suppress(AttributeError):
#                 setattr(self, key, value)
#         return found
#         # logger.success(found)

#     def save_current(self, record: dict = {}) -> Dataset[SupaModelT]:
#         try:
#             dump = (
#                 record if record else self.model_dump(exclude_none=True, by_alias=True)
#             )
#             saved = self.save_one(dump)
#             if saved.data:
#                 self.id = saved[0].id
#             else:
#                 return saved
#         except Exception:
#             raise

#     @classmethod
#     def save_one(cls, record: dict = {}) -> Dataset[SupaModelT]:
#         if not record:
#             raise ValueError(
#                 "No data to save. Please provide a record with something in the dictionary."
#             )
#         dump_id = record.pop("id", None)
#         if dump_id:
#             query_fn = cls.table.upsert
#             record = {**record, "id": str(dump_id)}
#         else:
#             query_fn = cls.table.insert

#         serialize_dict(record)
#         query = query_fn(record)
#         # logger.debug(query)
#         # logger.warning(cls.table_name())
#         return cls.extract(query)

#     @classmethod
#     def save_many(cls, records: list[dict] = []) -> Dataset[SupaModelT]:
#         if not records:
#             raise ValueError(
#                 "No data to save. Please provide a record with something in the dictionary."
#             )
#         if not isinstance(records, list) or not all(
#             isinstance(record, dict) for record in records
#         ):
#             raise ValueError("Please provide a list of records to save.")
#         all_ids = in_all_dicts(records, "id")
#         query_fn = cls.table.insert if not all_ids else cls.table().upsert

#         query = query_fn(records)
#         return cls.extract(query)

#     def delete(self, id: str | None = None) -> Dataset[SupaModelT]:
#         try:
#             delete_id = id if id is not None else self.id
#             return self.delete_one(delete_id)
#         except Exception as e:
#             raise e

#     @classmethod
#     def delete_one(cls, id: str | None = None) -> SupaModelT:

#         query = cls.table.delete().eq("id", id)
#         return cls.extract(query)

#     # Delete many records by id
#     @classmethod
#     def delete_many(cls, ids: list[str] = []) -> Dataset[SupaModelT]:
#         if not ids or not isinstance(ids, list):
#             raise ValueError("No ids to delete. Please provide a list of ids.")
#         query = cls.table.delete().in_("id", ids)
#         return cls.extract(query)

#     @classmethod
#     def list_all(cls) -> Dataset[SupaModelT]:

#         with contextlib.suppress(Exception):
#             builder = cls.table.select("*")
#             return cls.extract(builder)
#         return cls.dataset(data=[])

#     @classmethod
#     def list_paginated(cls, page: int = 0, per_page: int = 50) -> Dataset[SupaModelT]:
#         with contextlib.suppress(Exception):
#             response = cls.table.select("*").range(page, per_page).execute()
#             return cls.dataset(data=response.data)
#         return cls.dataset(data=[])
#         # except Exception as e:
#         #     raise e

#     @model_validator(mode="before")
#     @classmethod
#     def validate_model(cls, values: Any) -> Any:
#         return values

#     @classmethod
#     def find_one(cls, query_params: dict = {}, ordering=True) -> SupaModelT | None:

#         query = cls.select_eq(inputs=query_params)
#         query = query.limit(1)
#         dataset = cls.extract(query)
#         if not dataset.empty():
#             return dataset[0]
#         return None


# def main():
#     print("Hello, World!")


# if __name__ == "__main__":
#     main()
