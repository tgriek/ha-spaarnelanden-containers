from __future__ import annotations

from homeassistant import config_entries
import voluptuous as vol
from .const import CONF_CONTAINERS, DOMAIN

class SpaarnelandenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            raw = user_input[CONF_CONTAINERS]
            containers = [
                c.strip() for c in raw.split(",") if c.strip()
            ]

            if not containers:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._schema(raw),
                    errors={"base": "no_containers"},
                )

            return self.async_create_entry(
                title="Spaarnelanden Containers",
                data={
                    CONF_CONTAINERS: containers
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(""),
        )

    @staticmethod
    def _schema(default_value: str) -> vol.Schema:
        return vol.Schema({vol.Required(CONF_CONTAINERS, default=default_value): str})
