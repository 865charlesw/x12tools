from pathlib import Path
from typing import Type, Self, Optional
from dataclasses import dataclass

from .segment import X12Segment
from .constants import ELEMENT_SEPARATOR_INDEX, SEGMENT_TERMINATOR_INDEX


@dataclass
class X12Document:
    """
    Represents an X12 document.

    Attributes
    ----------
    segments : list of X12Segment
        The segments within the X12 document.
    segment_terminator : str, optional
        The character used to terminate segments (default is "~").
    element_separator : str, optional
        The character used to separate data elements (default is "*").
    """

    segments: list[X12Segment]
    segment_terminator: str = "~"
    element_separator: str = "*"
    file_path: Optional[Path] = None

    @classmethod
    def from_string(cls: Type[Self], content: str) -> Self:
        """
        Creates an X12File instance from a string.

        Parameters
        ----------
        content : str
            A string (or castable to str) representing the X12 document.

        Returns
        -------
        Self
            An instance of X12File.
        """
        content = str(content)
        content = content.strip()
        element_separator = content[ELEMENT_SEPARATOR_INDEX]
        segment_terminator = content[SEGMENT_TERMINATOR_INDEX]
        content = content.removesuffix(segment_terminator)
        segments = content.split(segment_terminator)
        segments = [
            X12Segment.from_string(segment, element_separator) for segment in segments
        ]
        return cls(
            segments=segments,
            segment_terminator=segment_terminator,
            element_separator=element_separator,
        )

    @classmethod
    def from_file(cls: Type[Self], file_path: str | Path) -> Self:
        """
        Creates an X12File instance from a file.

        Parameters
        ----------
        file_path : str or Path
            The path to the file to read.

        Returns
        -------
        Self
            An instance of X12File.
        """
        file_path = Path(file_path)
        file_content = file_path.read_text()
        obj = cls.from_string(file_content)
        obj.file_path = Path(file_path)
        return obj

    def get_segments(
        self, filters: str | list[str] | dict[int, str]
    ) -> list[tuple[int, X12Segment]]:
        """
        Returns a list of segments that match the filters.

        Parameters
        ----------
        filters : str, list of str, or dict of int to str
            A single regex pattern to match segments' identifiers against. Or a list of
            patterns to match segments' elements against, in order (identifier first).
            Or a dictionary where keys are indexes of each element to match and values
            are patterns to match against.

        Returns
        -------
        list of tuple of int and X12Segment
            The segments that match the filters.
        """
        if isinstance(filters, str):
            filters = [filters]
        if isinstance(filters, list):
            filters = dict(enumerate(filters))
        return [
            (idx, segment)
            for idx, segment in enumerate(self.segments)
            if segment.matches(filters)
        ]

    def remove(self, filters: str | list[str] | dict[int, str], single=True) -> int:
        """
        Removes segments that match the filters.

        Parameters
        ----------
        filters : str, list of str, or dict of int to str
            Filters to pass to get_segments.

        Returns
        -------
        int
            The number of segments removed.
        """
        segments = (
            [self.get_single_segment(filters)] if single else self.get_segments(filters)
        )
        for idx, segment in reversed(segments):
            self.segments.pop(idx)
        return len(segments)

    def get_single_segment(
        self, filters: str | list[str] | dict[int, str]
    ) -> tuple[int, X12Segment]:
        """
        Returns a single segment (with index) that matches the filters.

        Parameters
        ----------
        filters : str, list of str, or dict of int to str
            Filters to pass to get_segments.

        Returns
        -------
        tuple of int and X12Segment
            The index and segment that matches the filters.

        Raises
        ------
        KeyError
            If no segment or more than one matches the filters.
        """
        filtered = self.get_segments(filters)
        if len(filtered) != 1:
            raise KeyError(
                f"{len(filtered)} segments found for filters {repr(filters)}"
            )
        return filtered[0]

    def __getitem__(self, key: int | str) -> X12Segment:
        """
        Returns a single segment by regex pattern.

        Parameters
        ----------
        key : int or str
            The index of the segment or the regex pattern to match against the segment's
            identifier.

        Returns
        -------
        X12Segment
            The segment that matches the key.
        """
        if isinstance(key, int):
            return self.segments[key]
        return self.get_single_segment(key)[1]

    def update_se_lengths(self) -> None:
        """
        Updates transaction set trailers to match the actual number of segments.
        """
        for st_idx, st in self.get_segments("ST"):
            control_number = st[2]
            se_idx, se = self.get_single_segment({0: "SE", 2: control_number})
            se[1] = str(se_idx - st_idx + 1)

    def to_string(self, newlines=None) -> str:
        """
        Returns the X12 file as a string, updating transaction set lengths.

        Parameters
        ----------
        newlines : None or bool, optional
            Whether to include newlines in the output. If None, newlines are included if
            the segment terminator does not already include a newline (default is None).

        Returns
        -------
        str
            The X12 file as a string.
        """
        self.update_se_lengths()
        segment_delimiter = self.segment_terminator
        if newlines or (newlines is None and "\n" not in segment_delimiter):
            segment_delimiter += "\n"
        segments = (
            segment.to_string(self.element_separator) for segment in self.segments
        )
        return segment_delimiter.join(segments) + segment_delimiter

    def to_file(self, file_path: str | Path = None, newlines=None) -> None:
        """
        Writes the X12 file to a file.

        Parameters
        ----------
        file_path : str or Path, optional
            The path to write the file to. If not provided, writes to the original file.

        newlines : None or bool, optional
            Newlines parameter to pass to to_string.

        Raises
        ------
        ValueError
            If no file_path is provided and no original file_path is set.
        """
        file_path = file_path or self.file_path
        if not file_path:
            raise ValueError("No file_path provided and no original file_path set")
        file_path = Path(file_path)
        file_path.write_text(self.to_string(newlines=newlines))
