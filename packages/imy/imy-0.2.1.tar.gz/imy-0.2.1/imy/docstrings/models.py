from __future__ import annotations

from dataclasses import dataclass
from typing import *  # type: ignore

from . import parsers

__all__ = [
    "Docstring",
    "FunctionParameter",
    "FunctionDocs",
    "ClassField",
    "ClassDocs",
]


@dataclass
class Docstring:
    """
    A generic docstring object.
    """

    summary: str | None
    details: str | None

    key_sections: dict[str, dict[str, str]]

    @staticmethod
    def from_string(
        docstring: str,
        *,
        key_sections: Iterable[str],
    ) -> Docstring:
        return parsers.parse_docstring(
            docstring,
            key_sections=key_sections,
        )


@dataclass
class FunctionParameter:
    name: str
    type: str | None
    default: str | None

    kw_only: bool

    collect_positional: bool
    collect_keyword: bool

    description: str | None


@dataclass
class FunctionDocs:
    """
    A docstring specifically for functions and methods.
    """

    name: str
    parameters: list[FunctionParameter]
    return_type: str | None
    synchronous: bool

    summary: str | None
    details: str | None

    raises: list[tuple[str, str]]  # type, description

    @staticmethod
    def from_function(func: Callable) -> FunctionDocs:
        return parsers.parse_function(func)


@dataclass
class ClassField:
    name: str
    type: str
    default: str | None

    description: str | None


@dataclass
class ClassDocs:
    """
    A docstring specifically for classes.
    """

    name: str
    attributes: list[ClassField]
    functions: list[FunctionDocs]

    summary: str | None
    details: str | None

    @staticmethod
    def from_class(typ: Type) -> ClassDocs:
        return parsers.parse_class(typ)
