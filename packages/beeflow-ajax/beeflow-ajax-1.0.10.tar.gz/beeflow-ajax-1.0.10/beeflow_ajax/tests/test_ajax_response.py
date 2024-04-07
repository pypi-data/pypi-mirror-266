"""copyright (c) 2021 Beeflow Ltd.

Author Rafal Przetakowski <rafal.p@beeflow.co.uk>"""
import json
import sys
from io import StringIO
from unittest import TestCase

from unittest_data_provider import data_provider

from beeflow_ajax.lib import AjaxResponse


class TestAjaxResponse(TestCase):
    datasource_for_tests = lambda: (  # noqa: E731
        # ("function name", {parameters to unpack}, expected result),
        ("alert", {"msg": "team"}, [{"cmd": AjaxResponse.ALERT, "data": "team"}]),
        (
            "alert_success",
            {"msg": "team", "title": "other"},
            [{"cmd": AjaxResponse.ALERT_SUCCESS, "data": "team", "title": "other"}],
        ),
        (
            "alert_error",
            {"msg": "team", "title": "other"},
            [{"cmd": AjaxResponse.ALERT_ERROR, "data": "team", "title": "other"}],
        ),
        (
            "alert_warning",
            {"msg": "team", "title": "other"},
            [{"cmd": AjaxResponse.ALERT_WARNING, "data": "team", "title": "other"}],
        ),
        (
            "alert_info",
            {"msg": "team", "title": "other"},
            [{"cmd": AjaxResponse.ALERT_INFO, "data": "team", "title": "other"}],
        ),
        (
            "debug",
            {"data": {"team": "team name", "title": "other"}},
            [
                {
                    "cmd": AjaxResponse.DEBUG,
                    "data": {"team": "team name", "title": "other"},
                }
            ],
        ),
        (
            "append",
            {"element": "#team", "value": "some value"},
            [{"cmd": AjaxResponse.APPEND, "data": "some value", "id": "#team"}],
        ),
        (
            "assign",
            {"element": "#team", "value": "some value"},
            [{"cmd": AjaxResponse.ASSIGN, "data": "some value", "id": "#team"}],
        ),
        (
            "redirect",
            {"url": "https://some.address.co.uk"},
            [
                {
                    "cmd": AjaxResponse.REDIRECT,
                    "data": None,
                    "url": "https://some.address.co.uk",
                }
            ],
        ),
        (
            "reload_location",
            None,
            [{"cmd": AjaxResponse.RELOAD_LOCATION, "data": None}],
        ),
        (
            "remove",
            {"element": "#element_id"},
            [{"cmd": AjaxResponse.REMOVE, "data": None, "id": "#element_id"}],
        ),
        (
            "add_class",
            {"element": "#element_id", "class_name": "some-class"},
            [
                {
                    "cmd": AjaxResponse.ADD_CLASS,
                    "data": "some-class",
                    "id": "#element_id",
                }
            ],
        ),
        (
            "remove_class",
            {"element": "#element_id", "class_name": "some-class"},
            [
                {
                    "cmd": AjaxResponse.REMOVE_CLASS,
                    "data": "some-class",
                    "id": "#element_id",
                }
            ],
        ),
        (
            "set_class",
            {"element": "#element_id", "class_name": "some-class"},
            [
                {"cmd": AjaxResponse.REMOVE_CLASS, "data": None, "id": "#element_id"},
                {
                    "cmd": AjaxResponse.ADD_CLASS,
                    "data": "some-class",
                    "id": "#element_id",
                },
            ],
        ),
        (
            "return_json",
            {"data": {"class_name": "some-class"}},
            {"class_name": "some-class"},
        ),
        (
            "return_json",
            {"data": {"errors": {"msg": "some-class"}}},
            {"msg": "some-class"},
        ),
        (
            "script",
            {"javascript": "some javascript"},
            [{"cmd": AjaxResponse.RUN_SCRIPT, "data": "some javascript"}],
        ),
        (
            "show",
            {"element": "#element"},
            [{"cmd": AjaxResponse.SHOW, "data": None, "id": "#element"}],
        ),
        (
            "hide",
            {"element": "#element"},
            [{"cmd": AjaxResponse.HIDE, "data": None, "id": "#element"}],
        ),
        (
            "insert_before",
            {"element": "#element", "value": "Some value"},
            [
                {
                    "cmd": AjaxResponse.INSERT_BEFORE,
                    "data": "Some value",
                    "id": "#element",
                }
            ],
        ),
        (
            "init_ajax_links",
            None,
            [{"cmd": AjaxResponse.INIT_AJAX_LINKS, "data": None}],
        ),
        (
            "init_ajax_select",
            None,
            [{"cmd": AjaxResponse.INIT_AJAX_SELECT, "data": None}],
        ),
        (
            "init_ajax_forms",
            None,
            [{"cmd": AjaxResponse.INIT_AJAX_FORMS, "data": None}],
        ),
        (
            "set_input_value",
            {"element": "#element_id", "value": "some value"},
            [
                {
                    "cmd": AjaxResponse.SET_INPUT_VALUE,
                    "data": "some value",
                    "id": "#element_id",
                }
            ],
        ),
        (
            "modal",
            {"element": "#element_id", "action": "some value"},
            [{"cmd": AjaxResponse.MODAL, "data": "some value", "id": "#element_id"}],
        ),
        (
            "set_url",
            {"element": "#element_id", "url": "https://some-url.com"},
            [
                {
                    "cmd": AjaxResponse.URL,
                    "data": "https://some-url.com",
                    "id": "#element_id",
                }
            ],
        ),
        (
            "set_form_action",
            {"element": "#element_id", "action": "https://some-url.com"},
            [
                {
                    "cmd": AjaxResponse.SET_FORM_ACTION,
                    "data": "https://some-url.com",
                    "id": "#element_id",
                }
            ],
        ),
        (
            "load_script",
            {"name": "script name", "callback": "callback function"},
            [
                {
                    "cmd": AjaxResponse.LOAD_SCRIPT,
                    "data": None,
                    "script": "script name",
                    "callback": "callback function",
                }
            ],
        ),
    )

    @data_provider(datasource_for_tests)
    def test_all(self, command: str, parameters: dict or None, expected: list):
        function_name = getattr(AjaxResponse(), command)
        response: AjaxResponse = (
            function_name(**parameters) if parameters else function_name()
        )
        self.assertEqual(response.get_list(), expected)
        self.assertEqual(len(response.get_json()), len(json.dumps(expected)))
        self.assertEqual(len(str(response)), len(json.dumps(expected)))

    def test_print_output(self):
        given = {"name": "script name", "callback": "callback function"}
        expected = (
            json.dumps(
                [
                    {
                        "cmd": AjaxResponse.LOAD_SCRIPT,
                        "data": None,
                        "script": "script name",
                        "callback": "callback function",
                    }
                ]
            )
            + "\n"
        )

        response: AjaxResponse = AjaxResponse().load_script(**given)

        capturedOutput = StringIO()
        sys.stdout = capturedOutput
        response.print_output()
        sys.stdout = sys.__stdout__

        self.assertEqual(len(capturedOutput.getvalue()), len(expected))
