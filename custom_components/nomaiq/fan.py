"""Fan platform for NOMA iQ ceiling fans."""
from __future__ import annotations

from typing import Any

import ayla_iot_unofficial.device
from homeassistant.components.fan import (
    DIRECTION_FORWARD,
    DIRECTION_REVERSE,
    FanEntity,
    FanEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import NomaIQConfigEntry
from .coordinator import NomaIQDataUpdateCoordinator
from .entity import NomaIQEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NomaIQConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up NOMA iQ ceiling fan entities."""
    coordinator: NomaIQDataUpdateCoordinator = entry.runtime_data
    entities = [
        NomaIQCeilingFan(coordinator, device)
        for device in coordinator.data
        if device.oem_model_number == "ceiling-fan"
        and "fan_control" in device.properties_full
        and "fan_speed" in device.properties_full
    ]
    async_add_entities(entities, update_before_add=False)


class NomaIQCeilingFan(NomaIQEntity, FanEntity):
    """Native Home Assistant fan entity for a NOMA iQ ceiling fan."""

    _attr_name = "Ceiling Fan"
    _attr_speed_count = 6
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED | FanEntityFeature.DIRECTION
    )

    def __init__(
        self,
        coordinator: NomaIQDataUpdateCoordinator,
        device: ayla_iot_unofficial.device.Device,
    ) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"nomaiq_fan_{device.serial_number}"

    @property
    def is_on(self) -> bool | None:
        device = self._current_device
        return bool(device.get_property_value("fan_control")) if device else None

    @property
    def percentage(self) -> int | None:
        device = self._current_device
        if not device:
            return None
        speed = int(device.get_property_value("fan_speed") or 0)
        return round(speed * 100 / self.speed_count) if speed else 0

    @property
    def current_direction(self) -> str | None:
        device = self._current_device
        if not device:
            return None
        return (
            DIRECTION_FORWARD
            if bool(device.get_property_value("fan_direction"))
            else DIRECTION_REVERSE
        )

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        await self._device.async_set_property_value("fan_control", 1)
        if percentage is not None:
            speed = max(1, min(self.speed_count, round(percentage * self.speed_count / 100)))
            await self._device.async_set_property_value("fan_speed", speed)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._device.async_set_property_value("fan_control", 0)
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        if percentage <= 0:
            await self.async_turn_off()
            return
        speed = max(1, min(self.speed_count, round(percentage * self.speed_count / 100)))
        await self._device.async_set_property_value("fan_control", 1)
        await self._device.async_set_property_value("fan_speed", speed)
        await self.coordinator.async_request_refresh()

    async def async_set_direction(self, direction: str) -> None:
        value = 1 if direction == DIRECTION_FORWARD else 0
        await self._device.async_set_property_value("fan_direction", value)
        await self.coordinator.async_request_refresh()
