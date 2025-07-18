import inspect
import os
import re
from datetime import datetime, timezone
from enum import Enum
from functools import singledispatch
from typing import Any, Mapping, Optional, Sequence, Type, Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict, SecretStr

from arize_toolkit.constants import MAX_RECURSION_DEPTH


@singledispatch
def _convert_to_dict(value, depth=0, exclude_none=False):
    """Default handler: return value as is if no specific type matches."""
    # Check depth here as well, although it's primarily relevant for recursive types
    if depth > MAX_RECURSION_DEPTH:
        return value
    return value


@_convert_to_dict.register(datetime)
def _(value, depth=0, exclude_none=False):
    """Handler for datetime objects."""
    # Depth check not strictly needed here, but good practice if structure changes
    # if depth > MAX_RECURSION_DEPTH: return value
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


@_convert_to_dict.register(Enum)
def _(value, depth=0, exclude_none=False):
    """Handler for Enum objects."""
    # if depth > MAX_RECURSION_DEPTH: return value
    return value.name


@_convert_to_dict.register(BaseModel)
def _(value, depth=0, exclude_none=False):
    """Handler for Pydantic BaseModel objects (recursive)."""
    if depth > MAX_RECURSION_DEPTH:
        return value  # Or perhaps return a placeholder like str(value)?
    # Use model_dump() which respects Pydantic settings
    dumped_dict = value.model_dump(exclude_none=exclude_none, by_alias=True)
    # Recursively convert the contents of the dumped dictionary
    return _convert_to_dict(dumped_dict, depth + 1, exclude_none)


@_convert_to_dict.register(dict)
def _(value, depth=0, exclude_none=False):
    """Handler for dict objects (recursive)."""
    if depth > MAX_RECURSION_DEPTH:
        return value
    return {k: _convert_to_dict(v, depth + 1, exclude_none) for k, v in value.items()}


@_convert_to_dict.register(list)
def _(value, depth=0, exclude_none=False):
    """Handler for list objects (recursive)."""
    if depth > MAX_RECURSION_DEPTH:
        return value
    return [_convert_to_dict(item, depth + 1, exclude_none) for item in value]


class Dictable(BaseModel):
    def to_dict(self, exclude_none: bool = False) -> dict:
        model_dict = self.model_dump(exclude_none=exclude_none, by_alias=True)
        return _convert_to_dict(model_dict, depth=0, exclude_none=exclude_none)


class GraphQLModel(Dictable):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore",  # Ignore extra fields
        validate_assignment=True,
        strict=False,  # Be lenient with types
        arbitrary_types_allowed=True,
        use_enum_values=False,  # Use enum names in serialization
    )

    @classmethod
    def to_graphql_fields(cls) -> str:
        def _get_field_string(model_class: Type[BaseModel], depth: int = 0, visited: Optional[set] = None) -> str:
            if visited is None:
                visited = set()

            # Create a path key based on class and depth to track recursion
            recursion_key = (model_class, depth)
            if recursion_key in visited:
                return ""
            visited.add(recursion_key)

            fields = []
            for field_name, field_info in model_class.model_fields.items():
                # Use the alias if it exists and has priority, otherwise use the field name
                graphql_name = field_info.alias if field_info.alias and field_info.alias_priority == 1 else field_name

                field_type = field_info.annotation
                base_type = field_type

                # Unwrap Optional
                if get_origin(field_type) is Union and type(None) in get_args(field_type):
                    base_type = next(t for t in get_args(field_type) if t is not type(None))

                # Handle Union types (non-Optional)
                if get_origin(base_type) is Union:
                    # For Union types, we need to collect all possible model fields
                    has_model_type = False
                    for union_type in get_args(base_type):
                        # Handle both direct model types and List[Model] types
                        if get_origin(union_type) is list:
                            list_type = get_args(union_type)[0]
                            if inspect.isclass(list_type) and issubclass(list_type, BaseModel):
                                has_model_type = True
                                nested_fields = _get_field_string(list_type, depth + 1, visited.copy())
                                if nested_fields:  # Only add if there are actual fields
                                    fields.append(f"{graphql_name} {{ {nested_fields} }}")
                                    continue
                        elif inspect.isclass(union_type) and issubclass(union_type, BaseModel):
                            has_model_type = True
                            nested_fields = _get_field_string(union_type, depth + 1, visited.copy())
                            if nested_fields:  # Only add if there are actual fields
                                fields.append(f"{graphql_name} {{ {nested_fields} }}")
                                continue

                    # If we haven't added any nested fields and there are no model types,
                    # treat as a regular field
                    if not has_model_type:
                        fields.append(graphql_name)
                    continue

                # Handle List types
                if get_origin(base_type) is list:
                    list_type = get_args(base_type)[0]
                    # If it's a List of models, expand the model fields
                    if inspect.isclass(list_type) and issubclass(list_type, BaseModel):
                        nested_fields = _get_field_string(list_type, depth + 1, visited.copy())
                        if nested_fields:  # Only add if there are actual fields
                            fields.append(f"{graphql_name} {{ {nested_fields} }}")
                            continue
                    # Otherwise treat as a regular field
                    fields.append(graphql_name)
                    continue

                # Check if it's a Pydantic model
                if inspect.isclass(base_type) and issubclass(base_type, BaseModel) and base_type != model_class:
                    nested_fields = _get_field_string(base_type, depth + 1, visited.copy())
                    if nested_fields:  # Only add if there are actual fields
                        fields.append(f"{graphql_name} {{ {nested_fields} }}")
                    else:
                        fields.append(graphql_name)
                else:
                    fields.append(graphql_name)

            return " ".join(fields)

        return _get_field_string(cls)

    @classmethod
    def to_mutation_fields(cls) -> str:
        visited = set()

        def _get_field_string(model_class: Type[BaseModel]) -> str:
            if model_class in visited:
                return ""
            visited.add(model_class)

            fields = []
            for field_name, field_info in model_class.model_fields.items():
                if field_name == "id" or field_name == "createdDate" or field_name == "updatedAt":
                    continue
                field_type = field_info.annotation
                base_type = field_type

                # Unwrap Optional
                if get_origin(field_type) is Union and type(None) in get_args(field_type):
                    base_type = next(t for t in get_args(field_type) if t is not type(None))

                    # Unwrap List
                if get_origin(base_type) is list:
                    base_type = get_args(base_type)[0]

                # Check if it's a Pydantic model
                if inspect.isclass(base_type) and issubclass(base_type, BaseModel) and base_type != model_class:
                    nested_fields = _get_field_string(base_type)
                    fields.append(f"{field_name}: {{ {nested_fields} }}")
                else:
                    fields.append(f"{field_name}: ${field_name}")

            return ", ".join(fields)

        return _get_field_string(cls)

    def to_variable_fields(self, max_depth: int = 2) -> dict:
        model_dict = self.model_dump()
        level = 0

        def _flat_dict(pre_dict: dict, level: int) -> dict:
            post_dict = {}
            for key, value in pre_dict.items():
                if isinstance(value, Enum):
                    post_dict[key] = value.name
                elif isinstance(value, datetime):
                    post_dict[key] = value.isoformat()
                elif isinstance(value, dict):
                    if level > max_depth:
                        post_dict[key] = None
                    else:
                        post_dict.update(_flat_dict(value, level + 1))
                else:
                    post_dict[key] = value
            return post_dict

        return _flat_dict(model_dict, level)


# Pattern handler registration system
class DatetimePatternHandler:
    """Helper class for registering datetime pattern handlers."""

    def __init__(self, pattern, parser_func, name=None):
        self.pattern = re.compile(pattern)
        self.parser = parser_func
        self.name = name or parser_func.__name__

    def matches(self, value: str) -> bool:
        return bool(self.pattern.match(value))

    def parse(self, value: str) -> datetime:
        dt = self.parser(value)
        # Ensure timezone is UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt


def parse_iso8601_z(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_iso8601(value: str) -> datetime:
    return datetime.fromisoformat(value)


def parse_ymd_div(value: str, div: str = "-") -> datetime:
    format_str = f"%Y{div}%m{div}%d"
    if len(value) > 10:
        format_str = f"%Y{div}%m{div}%d %H:%M:%S" if value.count(":") == 2 else f"%Y{div}%m{div}%d %H:%M"
    return datetime.strptime(value, format_str)


def parse_ymd_slash(value: str) -> datetime:
    return parse_ymd_div(value, "/")


def parse_ymd_dot(value: str) -> datetime:
    return parse_ymd_div(value, ".")


def parse_unix_timestamp(value: str) -> datetime:
    return datetime.fromtimestamp(int(value), tz=timezone.utc)


def parse_unix_milliseconds(value: str) -> datetime:
    return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)


def parse_date_with_div(value: str, div="/") -> datetime:
    """Parse dates with slash separators, intelligently determining format based on values."""
    # Extract day/month parts
    parts = value.split(div)
    first_num = int(parts[0])
    second_num = int(parts[1])

    # Determine format based on numeric ranges
    if first_num > 12 and 1 <= second_num <= 12:
        # First number can't be a month, must be DD/MM/YYYY
        format_str = f"%d{div}%m{div}%Y"
    elif 1 <= first_num <= 12 and second_num > 12:
        # First number is a valid month, second is too large for a month
        format_str = f"%m{div}%d{div}%Y"
    elif 1 <= first_num <= 12 and 1 <= second_num <= 12:
        # Both could be valid months or days
        # Default to MM/DD/YYYY for US format, but could be configurable
        format_str = f"%m{div}%d{div}%Y"

        # Optional: You could add logic to prefer a certain format based on context
        # For example: check if the resulting date is in the future/past
        # or use a global configuration setting
    else:
        # Handle edge cases
        format_str = f"%m{div}%d{div}%Y"  # Default

    # Add time components if present
    if len(value) > 10:
        time_suffix = " %H:%M:%S" if value.count(":") == 2 else " %H:%M"
        format_str += time_suffix

    try:
        return datetime.strptime(value, format_str)
    except ValueError:
        # If parsing fails with detected format, try the alternate
        alternate_format = f"%d{div}%m{div}%Y" if format_str.startswith("%m") else f"%m{div}%d{div}%Y"
        if len(value) > 10:
            alternate_format += format_str[format_str.index(" ") :]  # noqa: E203
        return datetime.strptime(value, alternate_format)


def parse_date_with_dashes(value: str) -> datetime:
    return parse_date_with_div(value, "-")


def parse_date_with_slashes(value: str) -> datetime:
    return parse_date_with_div(value, "/")


def parse_date_with_dots(value: str) -> datetime:
    return parse_date_with_div(value, ".")


class DatetimeParser:
    """Parse a string into a datetime object using pattern-based dispatch.

    This class provides a flexible way to parse various date/time formats into
    a datetime object. It supports ISO 8601, Unix timestamps, and various
    date/time formats with different separators.

    The class uses pattern-based dispatch to determine the appropriate parsing
    function for a given string. It supports various date/time formats, including:
    - ISO 8601 (with or without timezone offset)
    - Unix timestamps (10 or 13 digits)
    - Various date/time formats with different separators

    The class can be extended to add additional date/time formats to be recognized.

    Args:
        value: A string containing a date/time in a recognized format

    Returns:
        datetime: A UTC datetime object if parsing succeeds
        str: An error message if parsing fails

    """

    patterns = [
        DatetimePatternHandler(
            r"^\d{4}-\d{2}-\d{2}(?:[ T](\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)?)$",
            parse_iso8601_z,
        ),
        DatetimePatternHandler(
            r"^\d{4}-\d{2}-\d{2}(?:[ T](\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:?\d{2})?)?)?$",
            parse_iso8601,
        ),
        DatetimePatternHandler(
            r"^(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?$",
            parse_ymd_div,
        ),
        DatetimePatternHandler(
            r"^(\d{4})/(\d{1,2})/(\d{1,2})(?:[ T](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?$",
            parse_ymd_slash,
        ),
        DatetimePatternHandler(
            r"^(\d{4})\.(\d{1,2})\.(\d{1,2})(?:[ T](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?$",
            parse_ymd_dot,
        ),
        DatetimePatternHandler(r"^\d{10}$", parse_unix_timestamp),
        DatetimePatternHandler(r"^\d{13}$", parse_unix_milliseconds),
        DatetimePatternHandler(
            r"^(\d{1,2})/(\d{1,2})/(\d{2,4})(?:[ T](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?$",
            parse_date_with_slashes,
        ),
        DatetimePatternHandler(
            r"^(\d{1,2})-(\d{1,2})-(\d{2,4})(?:[ T](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?$",
            parse_date_with_dashes,
        ),
        DatetimePatternHandler(
            r"^(\d{1,2})\.(\d{1,2})\.(\d{2,4})(?:[ T](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?$",
            parse_date_with_dots,
        ),
    ]

    @singledispatch
    @classmethod
    def parse(cls, value: Any) -> datetime:
        return value

    @parse.register(str)
    def _(value: str) -> datetime:  # type: ignore
        for pattern in DatetimeParser.patterns:
            if pattern.matches(value):
                return pattern.parse(value)
        raise ValueError(f"Invalid datetime string, could not parse: {value}")

    @parse.register(datetime)
    def _(value: datetime) -> datetime:  # type: ignore
        return value

    @parse.register(int)
    def _(value: int) -> datetime:  # type: ignore
        return datetime.fromtimestamp(value, tz=timezone.utc)

    @parse.register(float)
    def _(value: float) -> datetime:  # type: ignore
        return datetime.fromtimestamp(value, tz=timezone.utc)

    @classmethod
    def run(cls, value: Any):
        return cls.parse(value)


# Public function that users will call
def parse_datetime(date_repr: Any) -> datetime:
    """Parse a string into a datetime object using pattern-based dispatch.

    Args:
        date_repr: A value containing a date/time in a recognized format

    Returns:
        datetime: A UTC datetime object if parsing succeeds
        str: An error message if parsing fails

    Examples:
        >>> parse_datetime("2023-04-01T12:30:45Z")
        datetime.datetime(2023, 4, 1, 12, 30, 45, tzinfo=timezone.utc)
        >>> parse_datetime("04/01/2023 12:30:45")
        datetime.datetime(2023, 4, 1, 12, 30, 45, tzinfo=timezone.utc)
        >>> parse_datetime("12/01/2023")
        datetime.datetime(2023, 1, 12, 0, 0, tzinfo=timezone.utc)
        >>> parse_datetime("2023-04-01")
        datetime.datetime(2023, 4, 1, 0, 0, tzinfo=timezone.utc)
        >>> parse_datetime("12.01.2023")
        datetime.datetime(2023, 1, 12, 0, 0, tzinfo=timezone.utc)
        >>> parse_datetime(1712985600)
        datetime.datetime(2024, 4, 15, 12, 0, 0, tzinfo=timezone.utc)
        >>> parse_datetime(1712985600.0)
        datetime.datetime(2024, 4, 15, 12, 0, 0, tzinfo=timezone.utc)

    """
    return DatetimeParser.run(date_repr)


class FormattedPrompt(Mapping[str, Any]):
    """Base class for formatted prompts that can be unpacked as kwargs
    to plug into LLM provider client libraries.

    This abstraction allows provider-specific formatted prompts to be
    used directly with their respective client libraries.
    """

    messages: Sequence[Any]
    kwargs: Mapping[str, Any]

    def __len__(self) -> int:
        return 1 + len(self.kwargs)

    def __iter__(self):
        yield "messages"
        yield from self.kwargs

    def __getitem__(self, key: str) -> Any:
        if key == "messages":
            return self.messages
        return self.kwargs[key]

    def __str__(self) -> Any:
        return self.messages


def get_key_value(env_name: str, key: Optional[str] = None) -> SecretStr:
    if key is None:
        if os.getenv(env_name) is None:
            raise ValueError(f"Environment variable {env_name} is not set")
        key = str(os.getenv(env_name))
    return SecretStr(key)
