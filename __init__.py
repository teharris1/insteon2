"""Support for INSTEON Modems (PLM and Hub)."""
import asyncio
import logging

from pyinsteon import async_close, async_connect, devices

from homeassistant.const import (
    CONF_HOST,
    CONF_PLATFORM,
    CONF_PORT,
    EVENT_HOMEASSISTANT_STOP,
)

from .const import (
    CONF_CAT,
    CONF_DIM_STEPS,
    CONF_FIRMWARE,
    CONF_HOUSECODE,
    CONF_HUB_PASSWORD,
    CONF_HUB_USERNAME,
    CONF_HUB_VERSION,
    CONF_IP_PORT,
    CONF_OVERRIDE,
    CONF_PRODUCT_KEY,
    CONF_SUBCAT,
    CONF_UNITCODE,
    CONF_X10,
    DOMAIN,
    INSTEON_COMPONENTS,
    ON_OFF_EVENTS,
)
from .schemas import CONFIG_SCHEMA  # noqa F440
from .utils import (
    add_on_off_event_device,
    async_register_services,
    get_device_platforms,
    register_new_device_callback,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up the connection to the modem."""
    insteon_modem = None

    conf = config[DOMAIN]
    port = conf.get(CONF_PORT)
    host = conf.get(CONF_HOST)
    ip_port = conf.get(CONF_IP_PORT)
    username = conf.get(CONF_HUB_USERNAME)
    password = conf.get(CONF_HUB_PASSWORD)
    hub_version = conf.get(CONF_HUB_VERSION)
    overrides = conf.get(CONF_OVERRIDE, [])
    x10_devices = conf.get(CONF_X10, [])

    async def get_all_status():
        """Get the current status of all Insteon devices."""
        for address in devices:
            device = devices[address]
            await device.async_status()

    async def id_unknown_devices():
        """Send device ID commands to all unidentified devices."""
        await get_all_status()
        _LOGGER.info("Identifying Insteon devices")
        await devices.async_load(id_devices=1)
        await devices.async_save(workdir=hass.config.config_dir)

    async def _close_insteon_connection(*args):
        """Close the Insteon connection."""
        await async_close()

    if host:
        _LOGGER.info("Connecting to Insteon Hub on %s:%d", host, ip_port)
        try:
            if not await async_connect(
                host=host,
                port=ip_port,
                username=username,
                password=password,
                hub_version=hub_version,
            ):
                return True
        except ConnectionError:
            _LOGGER.error("Could not connect to Insteon Hub")
            return True
        _LOGGER.info("Connection to Insteon Hub successful")
    else:
        _LOGGER.info("Connecting to Insteon PLM on %s", port)
        try:
            if not await async_connect(device=port):
                return True
        except ConnectionError:
            _LOGGER.error("Could not connect to Insteon PLM")
            return True
        _LOGGER.info("Connection to Insteon PLM successful")

    await devices.async_load(workdir=hass.config.config_dir, id_devices=0)

    register_new_device_callback(hass, config)
    async_register_services(hass)
    asyncio.create_task(id_unknown_devices())
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _close_insteon_connection)

    for device_override in overrides:
        #
        # Override the device default capabilities for a specific address
        #
        address = device_override.get("address")
        for prop in device_override:
            if prop in [CONF_CAT, CONF_SUBCAT]:
                insteon_modem.devices.add_override(address, prop, device_override[prop])
            elif prop in [CONF_FIRMWARE, CONF_PRODUCT_KEY]:
                insteon_modem.devices.add_override(
                    address, CONF_PRODUCT_KEY, device_override[prop]
                )

    for device in x10_devices:
        housecode = device.get(CONF_HOUSECODE)
        unitcode = device.get(CONF_UNITCODE)
        x10_type = "onoff"
        steps = device.get(CONF_DIM_STEPS, 22)
        if device.get(CONF_PLATFORM) == "light":
            x10_type = "dimmable"
        elif device.get(CONF_PLATFORM) == "binary_sensor":
            x10_type = "sensor"
        _LOGGER.debug(
            "Adding X10 device to Insteon: %s %d %s", housecode, unitcode, x10_type
        )
        device = insteon_modem.add_x10_device(housecode, unitcode, x10_type)
        if device and hasattr(device.groups[0x01], "steps"):
            device.groups[0x01].steps = steps

    _LOGGER.info("Setting up INSTEON platforms")
    _LOGGER.info("Insteon device count: %s", len(devices))
    for component in INSTEON_COMPONENTS:
        hass.async_create_task(
            hass.helpers.discovery.async_load_platform(component, DOMAIN, {}, config)
        )

    for address in devices:
        device = devices[address]
        platforms = get_device_platforms(device)
        # _LOGGER.info("Device: %s  Platforms: %s", str(address), str(platforms))
        if ON_OFF_EVENTS in platforms:
            add_on_off_event_device(hass, device)

    return True
