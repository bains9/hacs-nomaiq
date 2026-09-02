"""Platform for NomaIQ light integration."""

from __future__ import annotations

import asyncio
from typing import Any

import ayla_iot_unofficial.device
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import NomaIQConfigEntry
from .const import NATIVE_MODELS
from .coordinator import NomaIQDataUpdateCoordinator
from .entity import NomaIQEntity
from .factory import async_setup_mapped_platform

# The fan exposes five discrete colour-temperature positions.
# Kelvin values provide Home Assistant with a normal warmth control.
COLOR_TEMPERATURES = (2700, 3500, 4000, 5000, 6500)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NomaIQConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Noma IQ Light platform."""
    coordinator: NomaIQDataUpdateCoordinator = entry.runtime_data
    manager = coordinator.adoption

    for device in coordinator.data:
        if (
            device.oem_model_number in NATIVE_MODELS
            and not (
                manager
                and manager.is_forced(device.oem_model_number)
            )
            and "light_control" in device.properties_full
        ):
            async_add_entities(
                [NomaIQLightEntity(coordinator, device)],
                update_before_add=False,
            )

    await async_setup_mapped_platform(
        hass,
        entry,
        async_add_entities,
        Platform.LIGHT,
    )


class NomaIQLightEntity(NomaIQEntity, LightEntity):
    """NOMA iQ light with optional brightness and warmth controls."""

    def __init__(
        self,
        coordinator: NomaIQDataUpdateCoordinator,
        device: ayla_iot_unofficial.device.Device,
    ) -> None:
        super().__init__(coordinator, device)

        light_name = device.get_property_value("light_name")
        self._attr_name = light_name or device.name
        self._attr_unique_id = f"nomaiq_light_{device.serial_number}"
        self._attr_has_entity_name = bool(light_name)

        self._has_brightness = "light_rating" in device.properties_full
        self._has_color_temp = (
            "light_color_index" in device.properties_full
        )

        if self._has_color_temp:
            self._attr_supported_color_modes = {
                ColorMode.COLOR_TEMP
            }
            self._attr_min_color_temp_kelvin = (
                COLOR_TEMPERATURES[0]
            )
            self._attr_max_color_temp_kelvin = (
                COLOR_TEMPERATURES[-1]
            )
        elif self._has_brightness:
            self._attr_supported_color_modes = {
                ColorMode.BRIGHTNESS
            }
        else:
            self._attr_supported_color_modes = {
                ColorMode.ONOFF
            }

    @property
    def color_mode(self) -> ColorMode:
        if self._has_color_temp:
            return ColorMode.COLOR_TEMP
        if self._has_brightness:
            return ColorMode.BRIGHTNESS
        return ColorMode.ONOFF

    @property
    def is_on(self) -> bool | None:
        device = self._current_device
        return (
            bool(device.get_property_value("light_control"))
            if device
            else None
        )

    @property
    def brightness(self) -> int | None:
        if not self._has_brightness:
            return None

        device = self._current_device
        if not device:
            return None

        rating = int(
            device.get_property_value("light_rating") or 0
        )
        return round(max(0, min(100, rating)) * 255 / 100)

    @property
    def color_temp_kelvin(self) -> int | None:
        if not self._has_color_temp:
            return None

        device = self._current_device
        if not device:
            return None

        try:
            index = int(
                device.get_property_value("light_color_index")
            )
        except (TypeError, ValueError):
            return None

        if 1 <= index <= len(COLOR_TEMPERATURES):
            return COLOR_TEMPERATURES[index - 1]

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the native NOMA warmth position."""
        device = self._current_device
        return {
            "noma_light_color_index": (
                device.get_property_value("light_color_index")
                if device
                else None
            )
        }

    async def _async_wake_fan_controller(self) -> None:
        """Wake a ceiling-fan controller before sending a light command.

        Some controllers stop accepting cloud light commands after they have
        been idle, while a fan command makes the light channel responsive
        again. Re-sending the current fan state avoids changing the motor.
        """
        device = self._current_device or self._device
        if (
            "fan_control" not in device.properties_full
            or "fan_speed" not in device.properties_full
        ):
            return

        current_state = int(
            bool(device.get_property_value("fan_control"))
        )
        await device.async_set_property_value(
            "fan_control",
            current_state,
        )
        await asyncio.sleep(0.25)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_wake_fan_controller()
        await self._device.async_set_property_value(
            "light_control",
            1,
        )

        if self._has_brightness and ATTR_BRIGHTNESS in kwargs:
            rating = round(
                max(0, min(255, int(kwargs[ATTR_BRIGHTNESS])))
                * 100
                / 255
            )
            await self._device.async_set_property_value(
                "light_rating",
                rating,
            )

        if (
            self._has_color_temp
            and ATTR_COLOR_TEMP_KELVIN in kwargs
        ):
            requested = int(kwargs[ATTR_COLOR_TEMP_KELVIN])
            index = min(
                range(len(COLOR_TEMPERATURES)),
                key=lambda position: abs(
                    COLOR_TEMPERATURES[position] - requested
                ),
            ) + 1

            await self._device.async_set_property_value(
                "light_color_index",
                index,
            )

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_wake_fan_controller()
        await self._device.async_set_property_value(
            "light_control",
            0,
        )
        await self.coordinator.async_request_refresh()
