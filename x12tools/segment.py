import re
from typing import Type, Self

from .constants import ISA_ELEMENT_LENGTHS


class X12Segment(list[str]):
    """
    Represents a segment in an X12 file.
    """

    @classmethod
    def from_string(cls: Type[Self], content: str, element_separator: str) -> Self:
        """
        Creates an X12Segment instance from a string.

        Parameters
        ----------
        content : str
            The string content to parse.
        element_separator : str
            The character used to separate data elements.

        Returns
        -------
        Self
            An instance of X12Segment.
        """
        content = content.strip()
        return cls(content.split(element_separator))


    def matches(self, filters: dict[int, str]) -> bool:
        """
        Returns True if the segment matches the filter.

        Parameters
        ----------
        filters : dict of int to str
            The filters to apply to the segment, where the key is the index of the
            element and the value is the pattern to match.

        Returns
        -------
        bool
            True if the segment matches the filters.
        """
        filter_matches = (re.fullmatch(value, self[idx]) for idx, value in filters.items())
        return all(filter_matches)

    def to_string(self, element_separator: str) -> str:
        """
        Returns the segment as a string.

        Parameters
        ----------
        element_separator : str
            The character to use to separate data elements.

        Returns
        -------
        str
            The segment as a string.
        """
        if self[0] == "ISA":
            for idx, value in enumerate(self):
                stripped = value.rstrip()
                self[idx] = stripped.ljust(ISA_ELEMENT_LENGTHS[idx])
        return element_separator.join(self)
