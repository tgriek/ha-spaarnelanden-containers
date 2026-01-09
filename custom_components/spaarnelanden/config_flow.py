from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class SpaarnelandenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            raw = user_input["containers"]
            containers = [
                c.strip() for c in raw.split(",") if c.strip()
            ]

            return self.async_create_entry(
                title="Spaarnelanden Containers",
                data={
                    "containers": containers
                }
            )

        schema = vol.Schema({
            vol.Required(
                "containers",
                description={"suggested_value": ""}
            ): str
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "containers": "Comma-separated container IDs, e.g. 150484,20126"
            },
        )
