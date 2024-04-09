def calculate_overlap(start_1: int, end_1: int, start_2: int, end_2: int) -> int:
    """
    Calculates the overlap between two ranges.
    :param start_1: Start of the first range
    :param end_1: End of the first range
    :param start_2: Start of the second range
    :param end_2: End of the second range
    :return: Length of the overlap, can be negative if there is no overlap
    """

    if start_1 > end_1:
        raise ValueError(f'Start value ({start_1}) is greater end value ({end_1})')

    if start_2 > end_2:
        raise ValueError(f'Start value ({start_2}) is greater end value ({end_2})')

    overlap_start = max(start_1, start_2)
    overlap_end = min(end_1, end_2)
    overlap_length = overlap_end - overlap_start
    return overlap_length
