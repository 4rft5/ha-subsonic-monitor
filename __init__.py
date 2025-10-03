DOMAIN = "ha-subsonic-monitor"

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, ["media_player"])
    return True

async def async_unload_entry(hass, entry):
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return await hass.config_entries.async_forward_entry_unload(entry, "media_player")
