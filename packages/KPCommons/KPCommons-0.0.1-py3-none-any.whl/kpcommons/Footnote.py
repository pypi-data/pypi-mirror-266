from typing import List, Tuple
import re


def get_footnote_ranges_without_offset(input_text: str) -> List[Tuple[int, int]]:
    ranges, _ = get_footnote_ranges(input_text)
    return ranges


def get_footnote_ranges_with_offset(input_text: str) -> List[Tuple[int, int]]:
    _, ranges_with_offset = get_footnote_ranges(input_text)
    return ranges_with_offset


def get_footnote_ranges(input_text: str) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Takes a text and returns a list of tuples of start and end character positions of footnote ranges.
    :param input_text: The input text
    :return: A list of tuples of start and end character positions of footnote ranges
    """
    result: List[Tuple[int, int]] = []
    result_with_offset: List[Tuple[int, int]] = []

    offset = 0
    for re_match in re.finditer(r'\[\[\[((?:.|\n)+?)]]]', input_text):
        start = re_match.start()
        end = re_match.end()
        result.append((start, end))
        result_with_offset.append((start - offset, end - offset))
        offset += end - start

    return result, result_with_offset


def is_position_in_ranges(start: int, ranges: List[Tuple[int, int]]) -> bool:
    """
    Check if the given position is in one of the ranges.
    :param start: The position to check
    :param ranges: A list of tuples of start and end character positions of ranges
    :return: True if the position is in the ranges, otherwise False
    """
    for rf in ranges:
        if rf[0] <= start < rf[1]:
            return True

    return False


def is_range_in_ranges(start: int, end: int, ranges: List[Tuple[int, int]]) -> bool:
    """
    Check if the range given by the start and end positions overlaps with one of the given ranges.
    :param start: A start character position
    :param end: A end character position
    :param ranges: A list of tuples of start and end character positions of ranges
    :return: True if the start or end position is in the ranges, otherwise False
    """
    for rf in ranges:
        if (rf[0] <= start < rf[1]) or (rf[0] <= end <= rf[1]):
            return True

    return False


def remove_footnotes(input_text: str):
    result_text = re.sub(r'\[\[\[((?:.|\n)+?)]]]', '', input_text)
    return result_text


def map_to_real_pos(start, end, fn_ranges):
    start_offset = 0
    end_offset = 0

    for fn_range in fn_ranges:
        if fn_range[0] < start:
            start_offset += fn_range[1] - fn_range[0]
            end_offset += fn_range[1] - fn_range[0]
        elif fn_range[0] < end:
            end_offset += fn_range[1] - fn_range[0]
        else:
            break

    return start + start_offset, end + end_offset
