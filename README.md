# NOMA iQ for Home Assistant

An expanded fork of the unofficial NOMA iQ Home Assistant integration, using the Ayla IoT cloud.

## Tested ceiling-fan support

- Independent fan and light control
- Six fan-speed levels
- Forward and reverse direction
- Light brightness
- Five-step light colour temperature through Home Assistant's standard warmth control

The NOMA fan's native `light_color_index` values are mapped as follows:

| Native index | Home Assistant value |
| --- | --- |
| 1 | 2700 K (warmest) |
| 2 | 3500 K |
| 3 | 4000 K |
| 4 | 5000 K |
| 5 | 6500 K (coolest) |

Intermediate Kelvin selections snap to the nearest supported position.

## Other integration features

This working snapshot also includes dynamic device-property mappings, adoption support for unknown models, diagnostic sensors, repair reporting, and mapped entity platforms.

## Installation

Install as a custom repository through HACS, restart Home Assistant, and add the NOMA iQ integration using the credentials from the NOMA iQ app.

## Status

Ceiling-fan functionality was validated on Home Assistant 2026.8.3 with a NOMA iQ 52-inch smart ceiling fan. Other device models may expose different Ayla properties and should be tested independently.

## Attribution

Forked from [`mnfjorge/hacs-nomaiq`](https://github.com/mnfjorge/hacs-nomaiq). This project remains unofficial and is not affiliated with NOMA, Canadian Tire, Ayla Networks, or Home Assistant.
