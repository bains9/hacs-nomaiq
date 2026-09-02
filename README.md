# NOMA iQ for Home Assistant

An expanded, community-maintained fork of the unofficial NOMA iQ integration for Home Assistant. It connects to NOMA iQ devices through the Ayla IoT cloud and adds tested support for the NOMA iQ smart ceiling fan.

> This project is unofficial and is not affiliated with NOMA, Canadian Tire, Ayla Networks, or Home Assistant.

## Tested device support

| Device | Status | Available controls |
| --- | --- | --- |
| NOMA iQ 52-inch smart ceiling fan | Tested | Fan power, six speeds, forward/reverse direction, independent light power, brightness, five-step colour temperature |
| NOMA iQ garage-door opener | Inherited from upstream | Door control and opener light |
| Other NOMA iQ devices | Experimental | Dynamic entities may be created from properties exposed by the Ayla API |

Testing contributions for additional NOMA iQ models are welcome.

## Ceiling-fan light warmth

The ceiling fan exposes five discrete values through `light_color_index`. This fork presents them through Home Assistant's standard colour-temperature control.

| Native index | Home Assistant value |
| --- | --- |
| 1 | 2700 K — warmest |
| 2 | 3500 K |
| 3 | 4000 K |
| 4 | 5000 K |
| 5 | 6500 K — coolest |

Intermediate Kelvin selections snap to the nearest supported position. Brightness continues to use the fan's native `light_rating` property.

## Requirements

- Home Assistant
- HACS
- A working NOMA iQ account
- Devices already paired and working in the NOMA iQ mobile app
- Internet access from Home Assistant

This is a cloud-polling integration; local-only control is not currently available.

## Installation through HACS

1. Open **HACS → Integrations**.
2. Open the menu and select **Custom repositories**.
3. Add:

   ```text
   https://github.com/bains9/hacs-nomaiq
   ```

4. Select **Integration** as the category.
5. Install **NomaIQ**.
6. Restart Home Assistant.
7. Go to **Settings → Devices & services → Add integration**.
8. Search for **NomaIQ** and sign in with the same username and password used by the NOMA iQ app.

[![Open HACS repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bains9&repository=hacs-nomaiq&category=integration)

## Upgrading an existing installation

If NomaIQ is already installed from another custom repository:

1. Back up `/config/custom_components/nomaiq`.
2. Remove the old NomaIQ custom-repository entry from HACS.
3. Add this fork using the URL above.
4. Download the integration.
5. Restart Home Assistant.

Your Home Assistant config entry should normally remain in place, but keeping a backup is recommended before changing custom-integration sources.

## Troubleshooting

### Entities show unavailable

1. Confirm the device still works in the NOMA iQ mobile app.
2. If it is offline in the app, restore power or Wi-Fi connectivity first.
3. If it works in the app, reload NomaIQ from **Settings → Devices & services → NomaIQ → menu → Reload**.
4. If the entities remain unavailable, restart Home Assistant Core and review the NomaIQ log entries.

### Warmth control does not appear

Confirm that:

- this fork is the installed HACS source;
- the integration version is **2.1.0** or later;
- Home Assistant was restarted after installation; and
- the fan exposes the `light_color_index` property.

## Additional integration capabilities

The fork includes:

- native and dynamically mapped device platforms;
- adoption support for unknown device models;
- fan, light, cover, switch, select, number, sensor, binary-sensor, and humidifier platforms;
- diagnostic entities and repair reporting; and
- configurable property mappings.

Availability depends on the properties each device exposes through NOMA's Ayla account.

## Updating

HACS updates from this fork may replace locally edited files. Commit generally useful fixes here instead of maintaining untracked changes inside `custom_components`.

## Development and validation

The ceiling-fan implementation was validated using:

- Home Assistant 2026.8.3;
- a NOMA iQ 52-inch smart ceiling fan;
- physical verification of fan and light controls; and
- physical verification of all five colour-temperature positions.

Before installing modified source files, compile or validate the integration, run `ha core check`, and keep a rollback copy.

## Attribution

Originally forked from [mnfjorge/hacs-nomaiq](https://github.com/mnfjorge/hacs-nomaiq). The integration uses the unofficial `ayla_iot_unofficial` Python library.

Contributions, tested device reports, and focused pull requests are welcome.
