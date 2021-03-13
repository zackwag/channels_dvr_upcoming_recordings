"""The Channels DVR Recently Recorded integation."""

import aiohttp
import async_timeout
from homeassistant.const import CONF_HOST, CONF_PORT
import json
import logging
from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant


DOMAIN = "channels_dvr_recently_recorded"
STATUS_ENDPOINT = "/status"
VERSION = "version"

_LOGGER = logging.getLogger(__name__)


async def fetch(session, url):
    try:
        with async_timeout.timeout(8):
            async with session.get(url) as response:
                return await response.content.read()
    except:
        pass


async def request(url):
    async with aiohttp.ClientSession() as session:
        return await fetch(session, url)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the La Marzocco component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry):
    """Set up config entry."""
    status_uri = f"http://{config_entry.data[CONF_HOST]}:{config_entry.data[CONF_PORT]}{STATUS_ENDPOINT}"
    try:
        resp = await request(status_uri)
        json_string = resp.decode("utf-8")
        status = json.loads(json_string)
    except OSError:
        _LOGGER.warning("Host %s is not available", CONF_HOST)

    hass.data[DOMAIN][config_entry.entry_id] = {VERSION: status[VERSION]}

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(
        config_entry, "sensor"
    )

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok