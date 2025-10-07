from typing import TypeAlias, TYPE_CHECKING

if TYPE_CHECKING:
    BytesType: TypeAlias = bytearray | bytes
    Header: TypeAlias = tuple[bytes, int, int | None]


def headers(
    data: "BytesType", force: tuple["BytesType", ...] | None = None
) -> tuple["Header", ...]:
    headers: list["Header"] = []

    header_start: int = 0
    header_found: bool = False
    for i, char in enumerate(data):
        current_header: "BytesType" = data[header_start:i].strip()
        if force is not None and current_header in force:
            header_found = True

        if data[i] == 32:
            if len(data) > i + 1 and data[i + 1] == 32 and current_header:
                header_found = True
        elif header_found:
            headers.append((bytes(current_header), header_start, i))
            header_start = i
            header_found = False

    # Capture our final header if there is one.
    ending_header: "BytesType" = data[header_start:].strip()
    if ending_header:
        headers.append((bytes(ending_header), header_start, None))

    return tuple(headers)


def body(headers: tuple["Header", ...], line: "BytesType") -> dict[bytes, "BytesType"]:
    entry: dict[bytes, "BytesType"] = {}

    start_offset: int | None = 0
    for header_name, start_index, end_index in headers:
        if start_offset is None or start_index > len(line):
            break

        # If our data is shorter than our headers
        if end_index is not None:
            end_index: int = min(end_index, len(line))

        # If `end_index` is None, it indicates that we should capture everything remaining.
        # The end of our header being our space character indicates our simplest case
        # where we may potentially have fixed-width columns.
        header_start_offset: int = max(start_offset, start_index)
        if end_index is not None and (
            end_index <= start_offset or line[end_index - 1] != 32
        ):
            # Rather than strictly go off of our header indices, assume that continuous
            # data represents a singular column as it appears we might be overflowing.
            end_index: int = line.find(b"\x20", header_start_offset)
            end_index: int | None = None if end_index == -1 else end_index

        # Given we have established that our current offset is assigned to our current
        # header, we'll also assume that the whole chunk is associated as well.
        if line[header_start_offset] != 32:
            start_index: int = line.rfind(b"\x20", 0, header_start_offset)
            header_start_offset = None if start_index == -1 else start_index

        value: "BytesType" = line[header_start_offset:end_index].strip()
        if value:
            entry[header_name] = value

        start_offset = end_index

    return entry


__all__: tuple[str, ...] = ("headers", "body")
