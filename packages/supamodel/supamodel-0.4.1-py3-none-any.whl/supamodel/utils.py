"""
Utility functions and classes.

This module contains utility functions and classes that are used throughout the package. Many are general-purpose and can be used in other projects as well. If they prove their worth, they may be moved to a separate package in the future.

The kinds of utilities found in this module include:

1. Custom data structures
2. Decorators
3. File I/O utilities
4. General-purpose functions
5. Logging utilities
6. Math utilities
7. String utilities
8. System utilities
9. Type utilities
10. Async utilities

"""

import asyncio
import functools
import inspect
import re
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar, cast

import sniffio
from inflector import Inflector
from sniffio import current_async_library

# ---------------------------------------------------------
# Decorators
# ---------------------------------------------------------


class classproperty:
    """A decorator that allows a method to be accessed as a class property."""

    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


class cached_classproperty(classproperty):
    """
    A decorator that defines a class-level property with caching mechanism.

    This decorator can be used to define a class-level property that is computed
    once and then cached for subsequent access. It is similar to the `@property`
    decorator, but it works at the class level instead of the instance level.

    Usage:
        class MyClass:
            @cached_classproperty
            def my_property(cls):
                # Compute and return the value of the property

    Note:
        This decorator is a subclass of the `classproperty` decorator, which is
        a decorator that allows defining class-level properties in Python.

    Attributes:
        fget (function): The method that computes the value of the property.

    Methods:
        get_result_field_name(): Returns the name of the result field used for caching.
        __get__(instance, cls=None): Retrieves the value of the property.
        getter(method): Sets the method that computes the value of the property.

    """

    def __init__(self, method=None):
        self.fget = method

    def get_result_field_name(self):
        return self.fget.__name__ + "_property_result" if self.fget else None

    def __get__(self, instance, cls=None):
        result_field_name = self.get_result_field_name()

        if hasattr(cls, result_field_name):
            return getattr(cls, result_field_name)

        if not cls or not result_field_name:
            return self.fget(cls)

        setattr(cls, result_field_name, self.fget(cls))
        return getattr(cls, result_field_name)

    def getter(self, method):
        self.fget = method
        return self


# ---------------------------------------------------------
# Async utilities
# ---------------------------------------------------------


def is_async_env() -> bool:
    """
    Check if a function is an asynchronous function.

    Args:
        func (Callable): The function to check.

    Returns:
        bool: True if the function is asynchronous, otherwise False.
    """
    try:
        current_async_library()

    except sniffio._impl.AsyncLibraryNotFoundError:
        return False

    return True


def expose_dual_runtimes(func):
    """
    Decorator that allows a function to be executed either synchronously or asynchronously,
    depending on whether an event loop is running or not.

    If the decorated function is a coroutine function, it checks if an event loop is running.
    If an event loop is running, the function is called directly. Otherwise, it is run synchronously
    using the `asyncio.run()` function.

    If the decorated function is not a coroutine, it is called directly.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if inspect.iscoroutinefunction(func):
            is_async = is_async_env()
            if not is_async:
                return run_sync(func(*args, **kwargs))
            # If an event loop is running, call the function directly
            return func(*args, **kwargs)
        else:
            # If the decorated function is not a coroutine, call it directly
            return func(*args, **kwargs)

    return wrapper


"""Utilities for working with asyncio."""


T = TypeVar("T")

BACKGROUND_TASKS = set()


def create_task(coro):
    """
    Creates async background tasks in a way that is safe from garbage
    collection.

    See
    https://textual.textualize.io/blog/2023/02/11/the-heisenbug-lurking-in-your-async-code/

    Example:

    async def my_coro(x: int) -> int:
        return x + 1

    # safely submits my_coro for background execution
    create_task(my_coro(1))
    """  # noqa: E501
    task = asyncio.create_task(coro)
    BACKGROUND_TASKS.add(task)
    task.add_done_callback(BACKGROUND_TASKS.discard)
    return task


async def run_async(fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Runs a synchronous function in an asynchronous manner.

    Args:
        fn: The function to run.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The return value of the function.

    Example:
        Basic usage:
        ```python
        def my_sync_function(x: int) -> int:
            return x + 1

        await run_async(my_sync_function, 1)
        ```
    """

    async def wrapper() -> T:
        try:
            return await loop.run_in_executor(
                None, functools.partial(fn, *args, **kwargs)
            )
        except Exception:
            # propagate the exception to the caller
            raise

    loop = asyncio.get_event_loop()
    return await wrapper()


def run_sync(coroutine: Coroutine[Any, Any, T]) -> T:
    """
    Runs a coroutine from a synchronous context, either in the current event
    loop or in a new one if there is no event loop running. The coroutine will
    block until it is done. A thread will be spawned to run the event loop if
    necessary, which allows coroutines to run in environments like Jupyter
    notebooks where the event loop runs on the main thread.

    Args:
        coroutine: The coroutine to run.

    Returns:
        The return value of the coroutine.

    Example:
        Basic usage:
        ```python
        async def my_async_function(x: int) -> int:
            return x + 1

        run_sync(my_async_function(1))
        ```
    """
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            with ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coroutine)
                return future.result()
        else:
            return asyncio.run(coroutine)
    except RuntimeError:
        return asyncio.run(coroutine)


def run_sync_if_awaitable(obj: Any) -> Any:
    """
    If the object is awaitable, run it synchronously. Otherwise, return the
    object.

    Args:
        obj: The object to run.

    Returns:
        The return value of the object if it is awaitable, otherwise the object
        itself.

    Example:
        Basic usage:
        ```python
        async def my_async_function(x: int) -> int:
            return x + 1

        run_sync_if_awaitable(my_async_function(1))
        ```
    """
    return run_sync(obj) if inspect.isawaitable(obj) else obj


def make_sync(async_func):
    """
    Creates a synchronous function from an asynchronous function.
    """

    @functools.wraps(async_func)
    def sync_func(*args, **kwargs):
        return run_sync(async_func(*args, **kwargs))

    sync_func.__signature__ = inspect.signature(async_func)
    sync_func.__doc__ = async_func.__doc__
    return sync_func


class ExposeSyncMethodsMixin:
    """
    A mixin that can take functions decorated with `expose_sync_method`
    and automatically create synchronous versions.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        for method in list(cls.__dict__.values()):
            if callable(method) and hasattr(method, "_sync_name"):
                sync_method_name = method._sync_name
                setattr(cls, sync_method_name, method._sync_wrapper)


def expose_sync_method(name: str) -> Callable[..., Any]:
    """
    Decorator that automatically exposes synchronous versions of async methods.
    Note it doesn't work with classmethods.

    Args:
        name: The name of the synchronous method.

    Returns:
        The decorated function.

    Example:
        Basic usage:
        ```python
        class MyClass(ExposeSyncMethodsMixin):

            @expose_sync_method("my_method")
            async def my_method_async(self):
                return 42

        my_instance = MyClass()
        await my_instance.my_method_async() # returns 42
        my_instance.my_method()  # returns 42
        ```
    """

    def decorator(
        async_method: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @functools.wraps(async_method)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            coro = async_method(*args, **kwargs)
            return run_sync(coro)

        # Cast the sync_wrapper to the same type as the async_method to give the
        # type checker the needed information.
        casted_sync_wrapper = cast(Callable[..., T], sync_wrapper)

        # Attach attributes to the async wrapper
        setattr(async_method, "_sync_wrapper", casted_sync_wrapper)
        setattr(async_method, "_sync_name", name)

        # return the original async method; the sync wrapper will be added to
        # the class by the init hook
        return async_method

    return decorator


# ---------------------------------------------------------
# General-purpose functions
# ---------------------------------------------------------


def title_case(v: str) -> str:
    """Convert the value to title case."""
    split = v.split(" ")

    return " ".join([s.capitalize() for s in split])


def check_int(v: int) -> int:
    """Check if the value is an int."""
    try:
        return int(v)
    except ValueError as exc:
        raise TypeError("value must be an int") from exc


inflector = Inflector()


def pluralize(word):
    return inflector.pluralize(word)


def singularize(word):
    return inflector.singularize(word)


def tableize(word: str) -> str:
    return inflector.tableize(word)


def slugify(work: str) -> str:
    # Replace non-alphanumeric characters with hyphens
    slug = re.sub(r"[^a-zA-Z0-9]", "-", work)
    # Insert hyphens between camelCase words and convert to lower case
    slug = re.sub(r"(?<!^)(?=[A-Z][a-z])", "-", slug).lower()
    # Replace multiple consecutive hyphens with a single hyphen
    slug = re.sub(r"-+", "-", slug)

    return slug


def extract_first_word(s: str) -> str:
    s = s.strip()
    # Split the string into words using uppercase letters, underscores, or hyphens as separators
    words = re.split(r"(?=[A-Z])|_|-", s)
    # Return the first word in lowercase form
    return words[0].lower()
