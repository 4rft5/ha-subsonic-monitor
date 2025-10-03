import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class SubsonicMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=f"Subsonic - {user_input['username']}",
                data=user_input
            )

        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("server_url", default="http://localhost:4040"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)
