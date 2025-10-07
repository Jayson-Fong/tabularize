"""
Tests command-line functionality
"""

import argparse
import io
import json
import random
import string
import uuid
from typing import Sequence, TYPE_CHECKING, Optional
from unittest import mock

import pytest

import tabularize.main
import tabularize.__main__


if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from _pytest._py.path import LocalPath

    # noinspection PyProtectedMember
    from _pytest.monkeypatch import MonkeyPatch


def _generate_random_sequence(min_length: int = 1, max_length: int = 64) -> str:
    """
    Generates a random ASCII text sequence of variable length.

    :param min_length: Minimum length of the sequence.
    :param max_length: Maximum length of the sequence.
    :return: Random ASCII text sequence.
    """

    characters = string.ascii_letters + string.digits
    return "".join(
        random.choice(characters) for _ in range(random.randint(min_length, max_length))
    )


def _patch_stdin(
    monkeypatch: "MonkeyPatch",
    stdin: bytes,
    args: Optional[Sequence[str]] = None,
    namespace: Optional[argparse.Namespace] = None,
) -> tuple[str, str]:
    """
    Executes the program with standard input

    :param monkeypatch: Monkey patch.
    :param stdin: Standard input to provide.
    :param args: Arguments for `tabularize.main.main`.
    :param namespace: Namespace for `tabularize.main.main`.
    :return: Tuple of standard output and error.
    """

    # Patch in a fake standard input
    fake_stdin: mock.Mock = mock.Mock()
    fake_stdin.buffer = io.BytesIO(stdin)
    fake_stdin.isatty.return_value = False
    monkeypatch.setattr(tabularize.main.sys, "stdin", fake_stdin)

    # Capture standard output
    with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        with mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            tabularize.main.main(args, namespace)

    return mock_stdout.getvalue(), mock_stderr.getvalue()


def test_main() -> None:
    """
    Attempts to run __main__.py a random number of times.

    :return: None.
    """

    call_count: int = random.randint(1, 32)
    with mock.patch.object(tabularize.main, "main") as patch_main:
        for _ in range(call_count):
            with mock.patch.object(tabularize.__main__, "__name__", "__main__"):
                tabularize.__main__.init()

    assert patch_main.call_count == call_count


def test_stdin_standard(monkeypatch: "MonkeyPatch") -> None:
    """
    Runs parsing using standard input with a simple case.

    :param monkeypatch: Monkey patch.
    :return: None.
    """

    for _ in range(128):
        for data_type in (bytes, bytearray):
            key = _generate_random_sequence()
            value = _generate_random_sequence()

            stdout, stderr = _patch_stdin(
                monkeypatch, data_type(key.encode() + b"\n" + value.encode()), ("-",)
            )
            assert json.loads(stdout) == {key: value}, "Parsed output matches expected"
            assert not stderr.strip(), "Standard error is blank"


def test_stdin_padded(monkeypatch: "MonkeyPatch") -> None:
    """
    Runs parsing with a few blank lines before the header.

    :param monkeypatch: Monkey patch.
    :return: None.
    """

    for padding_length in range(1, 4):
        padding: bytes = b"\n" * padding_length
        for data_type in (bytes, bytearray):
            key = _generate_random_sequence()
            value = _generate_random_sequence()

            stdout, stderr = _patch_stdin(
                monkeypatch,
                data_type(padding + key.encode() + b"\n" + value.encode()),
                ("-",),
            )
            assert json.loads(stdout) == {key: value}, "Parsed output matches expected"
            assert not stderr.strip(), "Standard error is blank"


def test_stdin_blank(monkeypatch: "MonkeyPatch") -> None:
    """
    Runs parsing with a blank standard input.

    :param monkeypatch: Monkey patch.
    :return: None.
    """

    for padding_length in range(1, 16):
        padding: bytes = b"\n" * padding_length
        for data_type in (bytes, bytearray):
            stdout, stderr = _patch_stdin(monkeypatch, data_type(padding), ("-",))

            assert not stdout.strip(), "Standard output is blank with blank input"
            assert not stderr.strip(), "Standard error is blank with blank input"


def test_stdin_tty(monkeypatch: "MonkeyPatch") -> None:
    """
    Attempts to parse with standard input but with an attached TTY.

    :return: None.
    """

    fake_stdin: mock.Mock = mock.Mock()
    fake_stdin.buffer = io.BytesIO()
    fake_stdin.isatty.return_value = True
    monkeypatch.setattr(tabularize.main.sys, "stdin", fake_stdin)

    with pytest.raises(SystemExit) as e:
        with mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            tabularize.main.main(["-"])

    assert e.type is SystemExit
    assert e.value.code == 1
    assert (
        "Terminal is attached - cannot process standard input" in mock_stderr.getvalue()
    )


def test_cli_file_error() -> None:
    """
    Attempts to parse with a file that does not exist.

    :return: None.
    """

    file_name: str = str(uuid.uuid4())
    with mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
        with pytest.raises(SystemExit) as e:
            tabularize.main.main((file_name,))

    assert e.type is SystemExit
    assert e.value.code == 1
    assert f"Failed to process file: {file_name}" in mock_stderr.getvalue()


def test_file_parsing(tmpdir: "LocalPath") -> None:
    """
    Attempts to parse using a file with a simple case.

    :param tmpdir: Temporary directory.
    :return: None.
    """

    for _ in range(16):
        # noinspection PyTypeChecker
        file_path = tmpdir.join(str(uuid.uuid4()))

        key: str = _generate_random_sequence()
        value: str = _generate_random_sequence()

        # Write our test file
        with open(file_path, "w", encoding="ascii") as f:
            f.write(f"{key}\n{value}")

        with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                tabularize.main.main((file_path.strpath,))

        assert json.loads(mock_stdout.getvalue()) == {
            key: value
        }, "Parsed output matches expected"
        assert not mock_stderr.getvalue().strip(), "Standard error is blank"
