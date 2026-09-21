# A1570 integration examples
Examples for integration of A1570 EMAT OEM Ultrasonic Pulser-Receiver frontend unit

https://acs-international.com/instruments/emat/a1570-emat-oem/

This repository contains example scripts for programming the A1570 device via SCPI and REST API protocols.
The examples demonstrate how to initialize the device, calibrate probes, and perform measurements.

# Contents

* [Complete SCPI command reference](SCPI_REFERENCE.md) - Syntax and behavior of every command registered by the firmware
* [Read MCU diagnostic log](SCPI_Python/read_mcu_log.py) - Simple, extensively commented Python example with no external packages
* [Follow MCU diagnostic log](SCPI_Python/follow_mcu_log.py) - Continuously append newly arriving MCU log entries to a file
* [Measurement with MCU logging](SCPI_Python/thickness_measurement_with_mcu_log.py) - Configure and run a measurement while printing A-scan metadata and appending new MCU logs to a timestamped file
* [Thickness Measurement (Pulse Mode)](SCPI_Python/thickness_measurement_pulse.py) - Example of automatic thickness measurement using pulse magnet probes (e.g. S3950)
* [Thickness Measurement (Permanent Mode)](SCPI_Python/thickness_measurement_permanent.py) - Example of automatic thickness measurement using permanent magnet probes (e.g. S7394)
* [Thickness Measurement (Semiautomatic Permanent Mode)](SCPI_Python/thickness_measurement_semiautomatic_permanent.py) - Example of semiautomatic thickness measurement using permanent magnet probes (e.g. S7694)
* [Receive and Display Data](SCPI_Python/receive_data_show.py) - Example of receiving and displaying raw data from the device
* [Common Functions](SCPI_Python/common_functions.py) - Shared utility functions used by other examples
* [REST API](REST_API/REST-API.md) - Reference for REST API operations
