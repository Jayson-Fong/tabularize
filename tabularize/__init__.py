def headers(data: bytearray, force: tuple[bytes, ...] | None = None) -> tuple[tuple[bytes, int, int | None], ...]:
    headers: list[tuple[bytes, int, int | None]] = []

    header_start: int = 0
    header_found: bool = False
    for i, char in enumerate(data):
        if force is not None:
            current_header: bytearray = data[header_start:i].strip()
            if current_header in force:
                headers.append((bytes(current_header), header_start, i))
                header_start = i
                header_found = False

        if data[i:i + 2] == b"\x20\x20" and data[header_start:i].strip():
            header_found = True
            continue

        if header_found and data[i] != 32:
            headers.append((bytes(data[header_start:i].strip()), header_start, i))
            header_start = i
            header_found = False

    if data[header_start:].strip():
        headers.append((bytes(data[header_start:].strip()), header_start, None))

    return tuple(headers)


def body(headers: tuple[tuple[bytes, int, int | None], ...], line: bytearray) -> dict:
    entry: dict = {}

    start_offset: int = 0
    for header_name, start_index, end_index in headers:
        # What if our end index indicates we should capture everything?
        if end_index is None:
            value = line[start_offset:].strip()
            if value:
                entry[header_name] = bytes(value)

            return entry

        if end_index <= start_offset:
            continue

        # What if we break at our end index?
        if end_index > 0 and line[end_index - 1] == 32:
            value = line[start_offset:end_index].strip()
            if value:
                entry[header_name] = bytes(value)

            start_offset = end_index
            continue

        # What if our data extends beyond its header?
        break_point: int = line.find(b"\x20", max(start_index, start_offset))
        if break_point == -1:
            # It seems we're capturing everything?
            value = line[max(start_index, start_offset):].strip()
            if value:
                entry[header_name] = bytes(value)

            return entry
        else:
            value = line[max(start_index, start_offset):break_point].strip()
            if value:
                entry[header_name] = bytes(value)

            start_offset = break_point

    return entry
