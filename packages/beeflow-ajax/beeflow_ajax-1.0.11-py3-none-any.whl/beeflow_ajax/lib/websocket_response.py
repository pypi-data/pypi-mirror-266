"""copyright (c) 2014 - 2024 Beeflow Ltd.

Author Rafal Przetakowski <rafal.p@beeflow.co.uk>"""
import json
from typing import Any, Optional, Self

from beeflow_ajax.lib import AjaxResponse


class WebSocketResponse(AjaxResponse):
    INIT_WEBSOCKET_FORMS = "initWebsocketForms"

    async def send_json(
        self, v: Optional[dict[str, Any] | list[dict[str, Any]]] = None
    ):
        """This command is available only for the WebSockets."""
        if isinstance(v, dict):
            v = [v]

        self.commands.append(v or [])

        response = json.dumps((self.commands or []))
        self.commands = []

        await self.response_.send_json(response)

    def init_websocket_forms(self) -> Self:
        """Initialize WebSockets forms."""
        self._add_command(self.INIT_WEBSOCKET_FORMS)
        return self
