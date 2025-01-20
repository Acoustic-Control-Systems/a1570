# A1570 integration examples
Examples for integration of A1570 EMAT OEM Ultrasonic Pulser-Receiver frontend unit

https://acs-international.com/instruments/emat/a1570-emat-oem/

This repository contains example scripts for programming the A1570 device via SCPI protocol.
The examples demonstrate how to initialize the device, calibrate probes, and perform measurements.

# Contents

* [Thickness Measurement (Pulse Mode)](SCPI_Python/thickness_measurement_pulse.py) - Example of automatic thickness measurement using pulse magnet probes (e.g. S3950)
* [Thickness Measurement (Permanent Mode)](SCPI_Python/thickness_measurement_permanent.py) - Example of automatic thickness measurement using permanent magnet probes (e.g. S7394)
* [Thickness Measurement (Semiautomatic Permanent Mode)](SCPI_Python/thickness_measurement_semiautomatic_permanent.py) - Example of semiautomatic thickness measurement using permanent magnet probes (e.g. S7694)
* [Receive and Display Data](SCPI_Python/receive_data_show.py) - Example of receiving and displaying raw data from the device
* [Common Functions](SCPI_Python/common_functions.py) - Shared utility functions used by other examples
