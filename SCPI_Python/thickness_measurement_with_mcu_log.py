#!/usr/bin/env python3
"""Measure A-scans and append new MCU diagnostic messages to a text file.

The example follows a complete device session:

1. connect to the A1570 with PyVISA;
2. configure a small set of measurement parameters;
3. start measurement;
4. request one A-scan and any new MCU log pages in a loop;
5. stop measurement;
6. close the connection.

The acquired A-scans are not saved. Only simple metadata such as sample count,
minimum, maximum, average, host time, and transfer time is printed.

Install PyVISA and its pure-Python backend before running the script:

    python -m pip install pyvisa pyvisa-py

Then edit DEVICE_IP below if necessary and run:

    python thickness_measurement_with_mcu_log.py
"""

import csv
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import pyvisa as visa

# Reuse the same A1570 helpers as the other measurement examples. In
# particular, get_vector_from_SCPI() handles the IEEE binary block and removes
# the device's 28-byte vector header before returning the A-scan samples.
from common_functions import *


# ---------------------------------------------------------------------------
# Settings that an integrator will normally change
# ---------------------------------------------------------------------------

DEVICE_IP = "192.168.0.1"
SCPI_PORT = 5025

# Ten iterations with a two-second pause make this example run for about
# twenty seconds. Device response time adds a small amount to the total.
MEASUREMENT_COUNT = 10
PAUSE_BETWEEN_MEASUREMENTS_SECONDS = 2.0

# Measurement parameters. Adapt these values to the connected
# probe and application. They match the style of thickness_measurement.py.
PROBE_TYPE = "S7392"
TRIGGER_INTERVAL_SECONDS = 0.25
SOUND_VELOCITY_METERS_PER_SECOND = 3247
SOFTWARE_AVERAGING_COUNT = 13

# A new default file is created for every program start. The file is opened in
# append mode, so an explicitly reused name is extended rather than overwritten.
LOG_FILE_NAME = (
    "a1570_mcu_log_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
    + ".txt"
)


def parse_log_info(response):
    """Convert the comma-separated SYST:LOG:INFO? response into integers."""
    fields = next(csv.reader([response]))
    if len(fields) != 9 or fields[0] != "1":
        raise RuntimeError("Unexpected SYST:LOG:INFO? response: " + response)

    values = [int(value) for value in fields]
    return {
        "oldest": values[1],       # first page still available
        "next": values[2],         # first page that does not exist yet
        "boot": values[3],
        "dropped": values[4],
        "pending": values[5],
        "healthy": values[6],
        "clock_synced": values[7],
        "session": values[8],
    }


def decode_log_text(text):
    """Decode newline, carriage-return, and backslash escapes from one page."""
    result = []
    position = 0
    while position < len(text):
        character = text[position]
        if character == "\\" and position + 1 < len(text):
            position += 1
            escaped = text[position]
            result.append({"n": "\n", "r": "\r", "\\": "\\"}.get(
                escaped, "\\" + escaped
            ))
        else:
            result.append(character)
        position += 1
    return "".join(result)


def append_new_log_pages(instrument, log_file, next_page_to_read):
    """Append all currently committed pages and return the new page cursor.

    The MCU writes cached log records automatically. This function intentionally
    does not send LOG:FLUSH on every loop iteration because forced writes add
    flash traffic and may occasionally require a 4 KiB sector erase.
    """
    info = parse_log_info(instrument.query("SYSTem:LOG:INFO?"))

    # The journal is circular. If the reader falls behind, old pages may have
    # been overwritten. Resume at the oldest page that is still available.
    if next_page_to_read < info["oldest"]:
        log_file.write(
            f"# Pages before {info['oldest']} were overwritten before reading.\n"
        )
        next_page_to_read = info["oldest"]

    while next_page_to_read < info["next"]:
        response = instrument.query(
            f"SYSTem:LOG:READ? {next_page_to_read}"
        )
        fields = next(csv.reader([response]))

        if len(fields) != 3 or int(fields[0]) != next_page_to_read:
            raise RuntimeError("Unexpected SYST:LOG:READ? response: " + response)

        page_boot = int(fields[1])
        if page_boot == 0:
            # An empty page can occur when it is cleared, overwritten, or was
            # incomplete after a power failure. Continue with the next page.
            log_file.write(
                f"# Page {next_page_to_read} is unavailable.\n"
            )
        else:
            log_file.write(
                f"# page={next_page_to_read}, mcu_boot={page_boot}\n"
            )
            log_file.write(decode_log_text(fields[2]))
            if fields[2] and not fields[2].endswith("\\n"):
                log_file.write("\n")

        next_page_to_read += 1

    # Make new messages visible in the file immediately, even if the program
    # is interrupted later.
    log_file.flush()
    return next_page_to_read


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stdout,
    )
    logger = logging.getLogger("a1570-example")

    resource_manager = None
    instrument = None
    measurement_started = False
    log_path = Path(LOG_FILE_NAME)

    try:
        # -------------------------------------------------------------------
        # STEP 1: Connect through PyVISA
        # -------------------------------------------------------------------
        logger.info("Connecting to A1570 at %s:%d", DEVICE_IP, SCPI_PORT)
        resource_manager = visa.ResourceManager()
        instrument = resource_manager.open_resource(
            f"TCPIP::{DEVICE_IP}::{SCPI_PORT}::SOCKET"
        )

        # The A1570 terminates textual SCPI replies with CR/LF. Binary A-scan
        # transfers are handled separately by query_binary_values().
        instrument.read_termination = "\r\n"
        instrument.write_termination = "\r\n"
        instrument.encoding = "iso-8859-1"
        instrument.timeout = 10000  # milliseconds

        identification = instrument.query("*IDN?")
        logger.info("Connected device: %s", identification)

        # Empty old errors before configuration. read_error_queue() is shared
        # with the other examples in common_functions.py.
        while True:
            error_number, error_message = read_error_queue(instrument)
            if error_number == 0:
                break
            logger.warning(
                "Removing old device error %d: %s",
                error_number,
                error_message,
            )

        instrument.write("SYST:LOG:LEVEL 3")
        logger.info(
            "System log level set to: %s",
            instrument.query("SYST:LOG:LEVEL?"),
        )
        
        # Flush records produced during connection, then place
        # the cursor at the current end. The file will contain new log records
        # produced during measurement, rather than the device's older history.
        # instrument.write("SYSTem:LOG:FLUSh")
        initial_log_info = parse_log_info(
            instrument.query("SYSTem:LOG:INFO?")
        )
        next_log_page = initial_log_info["next"]

        # Opening with mode "a" is important: it appends if this filename
        # already exists. The generated timestamp normally makes it a new file.
        with log_path.open("a", encoding="utf-8", newline="\n") as log_file:
            log_file.write(
                f"# A1570 MCU log started {datetime.now().isoformat()}\n"
                f"# device={identification}\n"
                f"# mcu_boot={initial_log_info['boot']}, "
                f"esp_session={initial_log_info['session']}, "
                f"clock_synced={initial_log_info['clock_synced']}, "
                f"first_new_page={next_log_page}\n"
            )
            log_file.flush()
            logger.info("Appending MCU log messages to %s", log_path)

            # -------------------------------------------------------------------
            # STEP 2: Configure measurement parameters
            # -------------------------------------------------------------------
            logger.info("Configuring measurement")

            instrument.write("TRIGgering:MODE INTERNAL")
            trigger_mode = instrument.query("TRIGgering:MODE?")
            if trigger_mode != "INTERNAL":
                raise RuntimeError("Could not set internal trigger mode")

            instrument.write(
                f"TRIGgering:INTerval {TRIGGER_INTERVAL_SECONDS} S"
            )
            logger.info(
                "Trigger interval reported by device: %s s",
                instrument.query("TRIGgering:INTerval?"),
            )

            instrument.write("TRANsmitter:ENABle ON")
            logger.info(
                "Transmitter state: %s",
                instrument.query("TRANsmitter:ENABle?"),
            )

            instrument.write(f'SENSe:PROBe:TYPE "{PROBE_TYPE}"')
            configured_probe = instrument.query("SENSe:PROBe:TYPE?")
            if configured_probe != PROBE_TYPE:
                raise RuntimeError(
                    f"Requested probe {PROBE_TYPE}, received {configured_probe}"
                )
            logger.info("Probe type: %s", configured_probe)

            instrument.write(
                "SOURce:VELocity:SOUNd "
                f"{SOUND_VELOCITY_METERS_PER_SECOND}"
            )
            logger.info(
                "Sound velocity: %s m/s",
                instrument.query("SOURce:VELocity:SOUNd?"),
            )

            instrument.write(
                f"SENSe:SOAVerage:COUNt {SOFTWARE_AVERAGING_COUNT}"
            )
            instrument.write("SENSe:SOAVerage:ENABle ON")
            logger.info(
                "Software averages: %s; enabled: %s",
                instrument.query("SENSe:SOAVerage:COUNt?"),
                instrument.query("SENSe:SOAVerage:ENABle?"),
            )

            # ---------------------------------------------------------------
            # STEP 3: Start measurement
            # ---------------------------------------------------------------
            instrument.write("STARt:MEASurement")
            measurement_started = True
            logger.info("Measurement started")

            # Give the device enough time to acquire its first vector.
            time.sleep(1.0)

            # ---------------------------------------------------------------
            # STEP 4: Request measurement data and log pages in one loop
            # ---------------------------------------------------------------
            for measurement_number in range(1, MEASUREMENT_COUNT + 1):
                request_started = time.perf_counter()

                # The common helper sends FETCh:ARRay?, decodes the IEEE binary
                # block as signed 16-bit samples, and removes the device header.
                samples = get_vector_from_SCPI(instrument)
                transfer_seconds = time.perf_counter() - request_started

                if len(samples) > 0:
                    minimum = min(samples)
                    maximum = max(samples)
                    average = sum(samples) / len(samples)
                else:
                    minimum = maximum = average = 0

                # Display metadata only. The sample array is discarded when
                # the next loop iteration replaces the local variables.
                logger.info(
                    "A-scan %d/%d: host_time=%s, samples=%d, "
                    "min=%d, max=%d, average=%.2f, "
                    "transfer=%.3f s",
                    measurement_number,
                    MEASUREMENT_COUNT,
                    datetime.now().isoformat(timespec="milliseconds"),
                    len(samples),
                    minimum,
                    maximum,
                    average,
                    transfer_seconds,
                )

                # INFO? exposes only pages already committed by the MCU. A
                # partially filled page normally becomes visible within about
                # one second, so no forced flash write is needed here.
                next_log_page = append_new_log_pages(
                    instrument, log_file, next_log_page
                )

                time.sleep(PAUSE_BETWEEN_MEASUREMENTS_SECONDS)

            # ---------------------------------------------------------------
            # STEP 5: Stop measurement and collect the final cached log page
            # ---------------------------------------------------------------
            instrument.write("STOP:MEASurement")
            measurement_started = False
            logger.info("Measurement stopped")

            # Force only the final cached records to flash, then append them.
            instrument.write("SYSTem:LOG:FLUSh")
            next_log_page = append_new_log_pages(
                instrument, log_file, next_log_page
            )
            logger.info("Final MCU log page cursor: %d", next_log_page)

    except KeyboardInterrupt:
        logger.info("Stopped by user")
    finally:
        # -------------------------------------------------------------------
        # STEP 6: Always stop and disconnect, including after an exception
        # -------------------------------------------------------------------
        if instrument is not None:
            if measurement_started:
                try:
                    instrument.write("STOP:MEASurement")
                    logger.info("Measurement stopped during cleanup")
                except Exception as error:
                    logger.warning("Could not stop measurement: %s", error)

            instrument.close()
            logger.info("SCPI connection closed")

        if resource_manager is not None:
            resource_manager.close()


if __name__ == "__main__":
    main()
