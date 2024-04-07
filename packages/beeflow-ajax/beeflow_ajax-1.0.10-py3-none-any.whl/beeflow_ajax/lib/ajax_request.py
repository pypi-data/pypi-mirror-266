"""copyright (c) 2014 - 2024 Beeflow Ltd.

Author Rafal Przetakowski <rafal.p@beeflow.co.uk>"""
import ast
from urllib.parse import unquote


class AjaxFormRequest:
    def __init__(self, request):
        data_str = unquote(request.body.decode()).replace("data=", "").replace("+", " ")
        self._request_data: dict = ast.literal_eval(data_str)

    @property
    def data(self) -> dict:
        return self._request_data
