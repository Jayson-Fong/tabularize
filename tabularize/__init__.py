BytesType = bytearray | bytes
Header: type = tuple[bytes, int, int | None]


def headers(
    data: BytesType, force: tuple[BytesType, ...] | None = None
) -> tuple[Header, ...]:
    headers: list[Header] = []

    header_start: int = 0
    header_found: bool = False
    for i, char in enumerate(data):
        current_header: BytesType = data[header_start:i].strip()
        if force is not None:
            if current_header in force:
                header_found = True

        if data[i : i + 2] == b"\x20\x20" and current_header:
            header_found = True
            continue

        if header_found and data[i] != 32:
            headers.append((bytes(current_header), header_start, i))
            header_start = i
            header_found = False

    if data[header_start:].strip():
        headers.append((bytes(data[header_start:].strip()), header_start, None))

    return tuple(headers)


def body(headers: tuple[Header, ...], line: BytesType) -> dict:
    entry: dict = {}

    start_offset: int = 0
    for header_name, start_index, end_index in headers:
        if start_offset is None:
            break

        # What if our end index indicates we should capture everything?
        # What if we break at our end index?

        # If `end_index` is None, it indicates that we should capture everything remaining.
        # The end of our header being our space character indicates our simplest case
        # where we may potentially have fixed-width columns.
        header_start_offset: int = max(start_offset, start_index)
        if end_index is None or (
            end_index > start_offset and line[end_index - 1] == 32
        ):
            pass
        else:
            # Rather than strictly go off of our header indices, assume that continuous
            # data represents a singular column as it appears we might be overflowing.
            end_index: int = line.find(b"\x20", header_start_offset)
            end_index: int | None = None if end_index == -1 else end_index

        value = line[header_start_offset:end_index].strip()
        if value:
            entry[header_name] = value

        start_offset = end_index

    return entry
