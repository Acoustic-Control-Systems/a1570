#!/usr/bin/env python3
"""Download the persistent MCU diagnostic log through SCPI.

Usage:
    python read_mcu_log.py 192.168.1.10
    python read_mcu_log.py 192.168.1.10 --output mcu-log.txt

The example uses only modules included with Python. It deliberately sends one
query at a time, which makes the request/reply sequence easy to understand and
safe for integrations that do not have an asynchronous SCPI framework.
"""

import argparse
import csv
import socket
from pathlib import Path


SCPI_PORT = 5025


def send_command(connection, command):
    """Send one complete SCPI command terminated as required by the A1570."""
    connection.sendall(command.encode("ascii") + b"\r\n")


class SocketLineReader:
    """Read CR/LF terminated replies without losing data after a newline.

    TCP is a byte stream: one recv() call may contain half a reply or several
    replies. Keeping unused bytes in ``buffer`` handles both cases.
    """

    def __init__(self, connection):
        self.connection = connection
        self.buffer = bytearray()

    def read_line(self):
        """Return one UTF-8 reply line without its CR/LF terminator."""
        while True:
            newline = self.buffer.find(b"\n")
            if newline >= 0:
                line = bytes(self.buffer[:newline])
                del self.buffer[: newline + 1]
                return line.rstrip(b"\r").decode("utf-8", errors="replace")

            block = self.connection.recv(2048)
            if not block:
                raise ConnectionError("The device closed the SCPI connection")
            self.buffer.extend(block)

            # A journal page is much smaller than this. The limit catches a
            # missing terminator instead of growing memory without a bound.
            if len(self.buffer) > 4096:
                raise RuntimeError("SCPI reply is too long or incomplete")


def read_query_reply(connection, replies, command):
    """Read and parse the CSV response belonging to a query command."""
    line = replies.read_line()
    try:
        # csv.reader correctly handles commas and doubled quotes inside the
        # quoted journal payload returned by SYST:LOG:READ?.
        return next(csv.reader([line]))
    except (csv.Error, StopIteration) as error:
        raise RuntimeError(
            f"Invalid response to {command}: {line!r}"
        ) from error


def decode_log_text(text):
    """Decode the three escapes used inside an MCU journal page.

    Unknown escapes are preserved. This avoids accidentally changing a message
    containing a Windows path or a backslash used by application diagnostics.
    """
    decoded = []
    position = 0
    while position < len(text):
        character = text[position]
        if character == "\\" and position + 1 < len(text):
            position += 1
            escaped = text[position]
            decoded.append({"n": "\n", "r": "\r", "\\": "\\"}.get(
                escaped, "\\" + escaped
            ))
        else:
            decoded.append(character)
        position += 1
    return "".join(decoded)


def download_log(device_address, output_path):
    """Download one bounded journal snapshot and return skipped-page count."""
    with socket.create_connection(
        (device_address, SCPI_PORT), timeout=10
    ) as connection:
        replies = SocketLineReader(connection)

        # FLUSH is a setter and therefore has no SCPI reply. It moves records
        # still cached in MCU RAM to flash before INFO? captures the range.
        send_command(connection, "SYST:LOG:FLUSH")

        send_command(connection, "SYST:LOG:INFO?")
        info = read_query_reply(connection, replies, "SYST:LOG:INFO?")
        if len(info) != 9 or info[0] != "1":
            raise RuntimeError("Unsupported log information: " + repr(info))

        oldest = int(info[1])       # first page to request
        next_page = int(info[2])    # exclusive upper bound
        boot = int(info[3])
        dropped = int(info[4])
        pending = int(info[5])
        healthy = int(info[6])
        clock_synced = int(info[7])
        session = int(info[8])

        # The MCU journal contains 1024 pages. Reject impossible bounds so a
        # damaged response cannot make this example run an enormous loop.
        if oldest > next_page or next_page - oldest > 1024:
            raise RuntimeError(f"Invalid log range: [{oldest}, {next_page})")

        skipped = 0
        with Path(output_path).open("w", encoding="utf-8", newline="\n") as output:
            output.write(
                f"# MCU log: boot={boot}, ESP session={session}, "
                f"clock_synced={clock_synced}, healthy={healthy}, "
                f"dropped_records={dropped}, cached_pages={pending}\n"
            )

            # Use the bounds read above even if new messages arrive. This makes
            # the download finite and gives the caller one consistent range.
            for page_number in range(oldest, next_page):
                command = f"SYST:LOG:READ? {page_number}"
                send_command(connection, command)
                page = read_query_reply(connection, replies, command)

                if len(page) != 3 or int(page[0]) != page_number:
                    raise RuntimeError("Unexpected page response: " + repr(page))

                page_boot = int(page[1])
                if page_boot == 0:
                    # A page may disappear if the circular journal wraps or is
                    # cleared while it is being downloaded.
                    skipped += 1
                    continue

                output.write(f"# page={page_number}, boot={page_boot}\n")
                output.write(decode_log_text(page[2]))

    return skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("device", help="A1570 IP address or host name")
    parser.add_argument(
        "--output", type=Path, default=Path("mcu-log.txt"),
        help="output text file (default: mcu-log.txt)",
    )
    arguments = parser.parse_args()

    skipped = download_log(arguments.device, arguments.output)
    print(f"Saved {arguments.output}; skipped pages: {skipped}")


if __name__ == "__main__":
    main()
