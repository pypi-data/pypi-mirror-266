"""Beeflow Ajax helps communicate HTML service with backend.

@author Rafal Przetakowski <rafal.p@beeflow.co.uk>"""

import json
from typing import Any, Dict, List, Optional, Self


class AjaxResponse:
    """Response object for AJAX."""

    ALERT = "alert"
    ALERT_SUCCESS = "alertSuccess"
    ALERT_ERROR = "alertError"
    ALERT_WARNING = "alertWarning"
    ALERT_INFO = "alertInfo"
    DEBUG = "debug"
    APPEND = "append"
    ASSIGN = "assign"
    APPEND_ELEMENT = "appendElement"
    ASSIGN_ELEMENT = "assignElement"
    APPEND_LIST = "appendList"
    ASSIGN_LIST = "assignList"
    REDIRECT = "redirect"
    RELOAD_LOCATION = "reloadLocation"
    REMOVE = "remove"
    ADD_CLASS = "addClass"
    REMOVE_CLASS = "removeClass"
    RUN_SCRIPT = "runScript"
    SHOW = "show"
    HIDE = "hide"
    INSERT_BEFORE = "insertBefore"
    INIT_AJAX_LINKS = "initAjaxLinks"
    INIT_AJAX_SELECT = "initAjaxSelect"
    INIT_AJAX_FORMS = "initAjaxForms"
    LOAD_SCRIPT = "loadScript"
    SET_INPUT_VALUE = "setInputValue"
    MODAL = "modal"
    URL = "setUrl"
    SET_FORM_ACTION = "setFormAction"
    SET_ATTRIBUTE = "setAttribute"

    def __init__(self, response=None):
        """Constructor prepares commands list."""
        self.commands = []
        self.response_ = response

    def __str__(self):
        """Returns json string."""
        return self.get_json()

    def response(self, *args, **kwargs):
        """
        Method returns response as the:
            * response (ex. HTTPResponse)
            * dictionary if we didn't pass any response object to the AjaxResponse initializer
        """
        commands = self.commands or {}
        self.commands = []

        if not self.response_:
            return commands

        return self.response_(commands, *args, **kwargs)

    def get_json(self) -> str:
        """Returns json string."""
        commands = self.commands or {}
        return json.dumps(commands)

    def print_output(self):
        """Prints json string."""
        print(self.get_json())

    def get_list(self) -> List:
        """Returns commands as a list."""
        return self.commands

    def alert(self, msg: str) -> Self:
        """Prepares alert command."""
        self._add_command(self.ALERT, {}, str(msg))
        return self

    def alert_success(
        self, msg: str, title: str = "", callback: Optional[str] = None
    ) -> Self:
        """Prepares success message command."""
        self._add_command(
            self.ALERT_SUCCESS, {"title": title, "callback": callback}, str(msg)
        )
        return self

    def alert_error(
        self, msg: str, title: str = "", callback: Optional[str] = None
    ) -> Self:
        """Prepares error message command."""
        self._add_command(
            self.ALERT_ERROR, {"title": title, "callback": callback}, str(msg)
        )
        return self

    def alert_warning(
        self, msg: str, title: str = "", callback: Optional[str] = None
    ) -> Self:
        """Prepares warning message command."""
        self._add_command(
            self.ALERT_WARNING, {"title": title, "callback": callback}, str(msg)
        )
        return self

    def alert_info(
        self, msg: str, title: str = "", callback: Optional[str] = None
    ) -> Self:
        """Prepares info message command."""
        self._add_command(
            self.ALERT_INFO, {"title": title, "callback": callback}, str(msg)
        )
        return self

    def debug(self, data) -> Self:
        """Prepares debug command."""
        self._add_command(self.DEBUG, {}, data)
        return self

    def append_element(self, element: str, element_data: dict[str:Any]) -> Self:
        self._add_command(self.APPEND_ELEMENT, {"id": element, "element": element_data})
        return self

    def assign_element(self, element: str, element_data: dict[str:Any]) -> Self:
        self._add_command(self.ASSIGN_ELEMENT, {"id": element, "element": element_data})
        return self

    def append_list(
        self, element: str, element_data: list[dict[str:Any]], list_type: str
    ) -> Self:
        self._add_command(
            self.APPEND_LIST,
            {"id": element, "element": element_data, "list_type": list_type},
        )
        return self

    def assign_list(
        self, element: str, element_data: list[dict[str:Any]], list_type: str
    ) -> Self:
        self._add_command(
            self.ASSIGN_LIST,
            {"id": element, "element": element_data, "list_type": list_type},
        )
        return self

    def append(self, element: str, value: str) -> Self:
        """Prepares append command which adds value to element.

        The element can be #id, .class or just tag ex. p
        """
        self._add_command(self.APPEND, {"id": element}, value)
        return self

    def assign(self, element: str, value: str) -> Self:
        """Prepares assign command which adds value to element.

        The element can be #id, .class or HTML tag.
        """
        self._add_command(self.ASSIGN, {"id": element}, value)
        return self

    def redirect(self, url: str) -> Self:
        """Redirect command for url redirection."""
        self._add_command(self.REDIRECT, {"url": url})
        return self

    def reload_location(self) -> Self:
        """Reload location command."""
        self._add_command(self.RELOAD_LOCATION)
        return self

    def remove(self, element: str) -> Self:
        """Removes element by #id, .class or HTML tag."""
        self._add_command(self.REMOVE, {"id": element})
        return self

    def add_class(self, element: str, class_name: str) -> Self:
        """Adds class to element which can be #id, .class or HTML tag."""
        self._add_command(self.ADD_CLASS, {"id": element}, class_name)
        return self

    def remove_class(self, element: str, class_name: str = None) -> Self:
        """Removes class from element which can be #id, .class or HTML tag."""
        self._add_command(self.REMOVE_CLASS, {"id": element}, class_name)
        return self

    def set_class(self, element: str, class_name: str) -> Self:
        """Sets new class on element which can be #id, .class or HTML tag."""
        self.remove_class(element)
        self.add_class(element, class_name)
        return self

    def return_json(self, data: Dict) -> Self:
        """Allows return json as a command."""
        try:
            self.commands = data["errors"]
        except KeyError:
            self.commands = data
        return self

    def script(self, javascript: str) -> Self:
        """Allows send javascript script to frontend."""
        self._add_command(self.RUN_SCRIPT, {}, javascript)
        return self

    def show(self, element: str) -> Self:
        """Shows element."""
        self._add_command(self.SHOW, {"id": element})
        return self

    def hide(self, element: str) -> Self:
        """Hides element."""
        self._add_command(self.HIDE, {"id": element})
        return self

    def insert_before(self, element: str, value: str) -> Self:
        """Inserts value before element."""
        self._add_command(self.INSERT_BEFORE, {"id": element}, value)
        return self

    def init_ajax_links(self) -> Self:
        """Initialize ajax links."""
        self._add_command(self.INIT_AJAX_LINKS)
        return self

    def init_ajax_select(self) -> Self:
        """Initialize ajax select."""
        self._add_command(self.INIT_AJAX_SELECT)
        return self

    def init_ajax_forms(self) -> Self:
        """Initialize ajax forms."""
        self._add_command(self.INIT_AJAX_FORMS)
        return self

    def load_script(self, name: str, callback: str) -> Self:
        """Allows load javascript script from file."""
        self._add_command(self.LOAD_SCRIPT, {"script": name, "callback": callback})
        return self

    def set_input_value(self, element: str, value: str) -> Self:
        self._add_command(self.SET_INPUT_VALUE, {"id": element}, value)
        return self

    def modal(self, element: str, action: str) -> Self:
        self._add_command(self.MODAL, {"id": element}, action)
        return self

    def set_url(self, element: str, url: str) -> Self:
        self._add_command(self.URL, {"id": element}, url)
        return self

    def set_form_action(self, element: str, action: str) -> Self:
        self._add_command(self.SET_FORM_ACTION, {"id": element}, action)
        return self

    def set_attribute(self, element: str, attribute_name: str, value: Any) -> Self:
        self._add_command(
            self.SET_ATTRIBUTE,
            {"id": element, "attribute": attribute_name, "value": value},
        )
        return self

    def _add_command(self, command: str, attributes: Dict = None, m_data=None) -> Self:
        """Adds command."""
        if attributes is None:
            attributes = {}

        attributes["cmd"] = command
        attributes["data"] = m_data
        self.commands.append(attributes)
        return self
