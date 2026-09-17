#!/usr/bin/env python3
"""Continuously append new A1570 MCU log entries to a local file.

Examples:
    python follow_mcu_log.py 192.168.1.10
    python follow_mcu_log.py 192.168.1.10 --output device.log --include-existing

Press Ctrl+C to stop. Only the Python standard library is required.
"""

import argparse
import socket
import sys
import time

from read_mcu_log import (
    SCPI_PORT,
    SocketLineReader,
    decode_log_text,
    read_query_reply,
    send_command,
)


def query_log_info(connection, replies):
    """Flush pending records and return the current log page bounds."""
    send_command(connection, "SYST:LOG:FLUSH")
    send_command(connection, "SYST:LOG:INFO?")
    info = read_query_reply(connection, replies, "SYST:LOG:INFO?")
    if len(info) != 9 or info[0] != "1":
        raise RuntimeError("Unexpected log information: " + repr(info))
    return {
        "oldest": int(info[1]),
        "next": int(info[2]),
        "boot": int(info[3]),
        "dropped": int(info[4]),
        "healthy": int(info[6]),
        "clock_synced": int(info[7]),
        "session": int(info[8]),
    }


def read_page(connection, replies, page_number):
    """Return a log page's boot number and decoded text."""
    command = f"SYST:LOG:READ? {page_number}"
    send_command(connection, command)
    page = read_query_reply(connection, replies, command)
    if len(page) != 3 or int(page[0]) != page_number:
        raise RuntimeError("Unexpected page reply: " + repr(page))
    return int(page[1]), decode_log_text(page[2])


def follow(device_address, output_path, poll_interval, include_existing):
    """Poll the device and append each newly available page once."""
    with socket.create_connection(
        (device_address, SCPI_PORT), timeout=10
    ) as connection:
        replies = SocketLineReader(connection)
        send_command(connection, "SYST:LOG:LEVEL 3")

        info = query_log_info(connection, replies)
        next_page = info["oldest"] if include_existing else info["next"]

        with open(output_path, "a", encoding="utf-8", newline="\n") as output:
            output.write(
                f"# Following MCU log: boot={info['boot']}, "
                f"ESP session={info['session']}, "
                f"clock_synced={info['clock_synced']}, "
                f"healthy={info['healthy']}, "
                f"dropped_records={info['dropped']}\n"
            )
            output.flush()

            while True:
                info = query_log_info(connection, replies)

                if next_page < info["oldest"] or next_page > info["next"]:
                    output.write(
                        f"# Log range changed; resuming at page "
                        f"{info['oldest']} (previous cursor={next_page})\n"
                    )
                    next_page = info["oldest"]

                while next_page < info["next"]:
                    page_boot, text = read_page(
                        connection, replies, next_page
                    )
                    if page_boot != 0:
                        output.write(
                            f"# page={next_page}, boot={page_boot}\n"
                        )
                        output.write(text)
                        if text and not text.endswith("\n"):
                            output.write("\n")
                        output.flush()
                    next_page += 1

                time.sleep(poll_interval)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("device_address", help="A1570 IP address or hostname")
    parser.add_argument(
        "--output", default="mcu_log.txt", help="file to append to"
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="seconds between polls (default: 1.0)",
    )
    parser.add_argument(
        "--include-existing",
        action="store_true",
        help="download the current backlog before following new entries",
    )
    args = parser.parse_args()
    if args.poll_interval <= 0:
        parser.error("--poll-interval must be greater than zero")
    return args


if __name__ == "__main__":
    arguments = parse_args()
    try:
        follow(
            arguments.device_address,
            arguments.output,
            arguments.poll_interval,
            arguments.include_existing,
        )
    except KeyboardInterrupt:
        print("Stopped.")
    except (OSError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
