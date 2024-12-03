import re
from typing import Type, Self

from .constants import ISA_PADS


class X12Segment(list[str]):
    """
    Represents a segment in an X12 file.
    """

    @classmethod
    def from_string(cls: Type[Self], content: str, data_element_separator: str) -> Self:
        """
        Creates an X12Segment instance from a string.

        Parameters
        ----------
        content : str
            The string content to parse.
        data_element_separator : str
            The character used to separate data elements.

        Returns
        -------
        Self
            An instance of X12Segment.
        """
        content = content.strip("\n")
        return cls(content.split(data_element_separator))


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
        return all(re.fullmatch(value, self[idx]) for idx, value in filters.items())

    def to_string(self, data_element_separator: str) -> str:
        """
        Returns the segment as a string.

        Parameters
        ----------
        data_element_separator : str
            The character to use to separate data elements.

        Returns
        -------
        str
            The segment as a string.
        """
        if self[0] == "ISA":
            for idx, value in enumerate(self):
                self[idx] = value.rstrip().ljust(ISA_PADS[idx])
        return data_element_separator.join(self)
