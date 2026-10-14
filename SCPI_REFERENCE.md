# A1570 SCPI command reference

The A1570 accepts SCPI commands over TCP port **5025**. Terminate every command
with `\r\n`. Queries end in `?` and return one response line unless the command
description says that vector data is returned.

## Reading the syntax

- Uppercase letters are the shortest accepted spelling: `SYSTem` accepts `SYST`.
- Square brackets mark optional path elements. `[:SOURce]:GAIN[:LEVel]?` accepts
  `GAIN?`, `SOUR:GAIN?`, and `SOURCE:GAIN:LEVEL?`.
- `<numeric>` means a number; `<string>` means text, normally in quotes.
- Boolean parameters accept `ON`/`OFF` and `1`/`0`.
- Numeric setters that support special values accept `MIN`, `MAX`, `DEF`, `UP`,
  and `DOWN`. The instrument validates its model-specific range.
- Use `SYSTem:ERRor[:NEXT]?` after a rejected command to read the error.

This list covers supported integration commands in the ESP32 firmware.

## MCU persistent log

Read a snapshot in this order: `FLUSH`, `INFO?`, then one `READ?` for each page
in `[oldest, next)`. The included [log example](SCPI_Python/read_mcu_log.py)
performs these steps.

| Command | Parameter or response | Description |
|---|---|---|
| `SYSTem:LOG:INFO?` | `version,oldest,next,boot,dropped,pending,healthy,synced,session` | Return metadata. `oldest` is inclusive and `next` is exclusive. |
| `SYSTem:LOG:READ? <sequence>` | `sequence,page_boot,"text"` | Read a page. `page_boot=0` means unavailable. Text escapes are `\n`, `\r`, and `\\`; quotes are doubled. |
| `SYSTem:LOG:CLEar` | none | Logically remove all currently visible pages. |
| `SYSTem:LOG:FLUSh` | none | Write cached MCU records to flash before a snapshot. |
| `SYSTem:LOG:LEVel?` | `0` to `3` | Read the persistent severity threshold. |
| `SYSTem:LOG:LEVel <level>` | `0` error, `1` warning, `2` info, `3` debug | Set the threshold until the MCU restarts. |

MCU messages use `M,<esp_session>,<display_ms>,<mcu_uptime_ms>,<level>,<message>`.
After startup synchronization, `display_ms` approximately matches the ESP32 log
timestamp. It is a millisecond boot-time clock, not UTC.

## IEEE 488.2 common commands

| Command | Description |
|---|---|
| `*CLS` | Clear status structures and the error queue. |
| `*ESE <mask>` / `*ESE?` | Set/query the Standard Event Status Enable register. |
| `*ESR?` | Read and clear the Standard Event Status register. |
| `*IDN?` | Return manufacturer, model, serial number, and firmware version. |
| `*SRE <mask>` / `*SRE?` | Set/query the Service Request Enable register. |
| `*STB?` | Read the status byte. |
| `*TST?` | Run the implemented self-test; `0` means success. |

## SYSTem and standard status

| Command | Description |
|---|---|
| `SYSTem:ERRor[:NEXT]?` | Remove and return the oldest error as `code,"message"`. |
| `SYSTem:ERRor:COUNt?` | Return the number of queued errors. |
| `SYSTem:VERSion?` | Return the supported SCPI standard version. |
| `STATus:QUEStionable[:EVENt]?` | Read and clear the questionable event register. |
| `STATus:QUEStionable:ENABle <mask>` / `...?` | Set/query its enable mask. |
| `STATus:PRESet` | Restore status-register enable masks to presets. |

## FETCh

| Command | Description |
|---|---|
| `FETCh[:ARRay]?` | Fetch the acquired A-scan array. Start acquisition first. |
| `[:FETCh]:RESult[:MEASure]?` | Fetch the latest thickness result. |

## SOURce

| Command | Parameter | Description |
|---|---|---|
| `[:SOURce]:GAIN[:LEVel]` / `...?` | numeric or special | Set/query receiver gain. |
| `[:SOURce]:GAIN:AUTO[:LEVel]?` | none | Return automatically selected gain. |
| `[:SOURce]:STARt[:ASCAN]` / `...?` | none | Start A-scan acquisition/query its state. |
| `[:SOURce]:STOP` | none | Stop acquisition. |
| `[:SOURce]:STARt:MEASurement` | none | Start automatic thickness measurement. |
| `[:SOURce]:STARt:MAXStrobe` | none | Start single-peak gate measurement. |
| `[:SOURce]:STARt:P2Peak` | none | Start peak-to-peak measurement. |
| `[:SOURce]:STARt:ACFStrobe` | none | Start autocorrelation gate measurement. |
| `[:SOURce]:STOP:MEASurement` | none | Stop thickness measurement. |
| `[:SOURce]:STARt:CALibration[:OBJect]` | none | Calibrate on the reference object. |
| `[:SOURce]:STARt:CALibration:AIR` | none | Calibrate in air. |
| `[:SOURce]:TRIGgering:INTerval` / `...?` | time or special | Set/query acquisition interval. |
| `[:SOURce]:TRIGgering:RATE` / `...?` | numeric or special | Set/query pulse repetition rate. |
| `[:SOURce]:TRIGgering:MODE` / `...?` | `INTernal` or `EXTernal` | Set/query triggering mode. |
| `[:SOURce]:FREQuency` / `...?` | numeric or special | Set/query input sampling frequency. |
| `[:SOURce]:TRANsmitter:PULSe[:LEVel]` / `...?` | numeric or special | Set/query pulse amplitude. |
| `[:SOURce]:TRANsmitter:FREQuency` / `...?` | frequency or special | Set/query burst frequency. |
| `[:SOURce]:TRANsmitter:PERiod` / `...?` | time or special | Set/query burst period. |
| `[:SOURce]:TRANsmitter:DURation` / `...?` | numeric or special | Set/query burst duration. |
| `[:SOURce]:TRANsmitter:ENABle` / `...?` | boolean | Enable/query the transmitter. |
| `[:SOURce]:TRANsmitter:MODE` / `...?` | mode | Set/query transducer polarity. |
| `[:SOURce]:DATA:LENGth?` | none | Query acquired vector length. |
| `[:SOURce]:VELocity[:SOUNd]` / `...?` | numeric or special | Set/query sound velocity. |
| `[:SOURce]:ZONDer:MODE` / `...?` | string | Set/query Zonder processing mode. |
| `[:SOURce]:SNDVector[:ENABle]` / `...?` | boolean | Include/query processed result vectors. |

## SENSe

| Command | Parameter | Description |
|---|---|---|
| `[:SENSe]:AVERage:COUNt` / `...?` | numeric or special | Set/query accumulation exponent A (0-4); acquisitions = 2^A. |
| `[:SENSe]:AVERage:PERiod` / `...?` | time or special | Set/query constant averaging interval. |
| `[:SENSe]:AVERage:PERiod:RANDom` / `...?` | time or special | Set/query random averaging interval. |
| `[:SENSe]:FILTer:HPASs[:NUMBer]` / `...?` | filter name | Select/query high-pass filter. |
| `[:SENSe]:MAGNet:DELay` / `...?` | time or special | Set/query magnet firing delay. |
| `[:SENSe]:MAGNet:ENABle` / `...?` | boolean | Enable/query the pulse magnet. |
| `[:SENSe]:MAGNet:VOLTage` / `...?` | numeric or special | Set/query magnet voltage. |
| `[:SENSe]:PROBe:DELay[:PROCessing]` / `...?` | numeric or special | Set/query processing delay. |
| `[:SENSe]:PROBe[:TYPE]` / `...?` | string | Set/query probe type. |
| `[:SENSe]:DEZones` / `...?` | string | Set/query encoded dead-zone data. |
| `[:SENSe]:CALibration:NOISe` / `...?` | string | Set/query encoded noise calibration. |
| `[:SENSe]:CALibration:EDARray` / `...?` | string | Set/query encoded eddy-current calibration. |
| `[:SENSe]:SOAVerage:COUNt` / `...?` | numeric or special | Set/query software averaging limit. |
| `[:SENSe]:SOAVerage[:ENABle]` / `...?` | boolean | Enable/query software averaging. |
| `[:SENSe]:STRObe:BEGin` / `...?` | numeric or special | Set/query measurement gate start. |
| `[:SENSe]:STRObe:WIDTh` / `...?` | numeric or special | Set/query measurement gate width. |
| `[:SENSe]:STRObe:LEVel` / `...?` | numeric or special | Set/query measurement gate threshold. |

Structured calibration strings are device-generated formats. Read the current
value before changing one, and consult the programming manual for their fields.

## MEMory and device STATus

| Command | Description |
|---|---|
| `MEMory:CLEar` | Compatibility command; currently a no-op. |
| `[:STATus]:BATTery?` | Return battery state of charge in percent. |
| `[:STATus]:CHSTatus?` | Return charging status. |
| `[:STATus]:PROBe:TEMPerature?` | Return EMAT pulse-magnet probe temperature. |

## Small TCP example

```python
import socket

with socket.create_connection(("192.168.1.10", 5025), timeout=10) as device:
    device.sendall(b"*IDN?\r\n")
    print(device.makefile("r", encoding="utf-8").readline().strip())
```
