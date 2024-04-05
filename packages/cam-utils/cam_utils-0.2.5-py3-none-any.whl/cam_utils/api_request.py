import json

import requests
from cam_utils.valida_info import ValidaInfo


class APIRequest:
    """Classe de Requisicao via API"""

    __method: str
    __url: str
    __body: json
    __headers: json
    __result: bool
    __data: []
    __respcode: int
    __respstatus: str
    __auth: any

    def __init__(self, metodo, url, bodyjson: json, headers: json):
        """Inicializa classe de Requisicao HTTP"""
        valida = ValidaInfo()
        self.__result = False
        self.__method = metodo.upper()
        if self.__method != "GET" and self.__method != "POST":
            raise ValueError(f"API Método nao valido {self.__method}.")

        if url == "":
            raise ValueError("API URL vazio.")
        elif not valida.url(url):
            raise ValueError(f"API URL nao valido {self.__url}.")
        else:
            self.__url = url

        self.__body = bodyjson
        self.__headers = headers

    def exec(self):
        """Realiza requisicao GET/POST no Servidor Informado"""
        print(self.__method)
        if self.__method == "GET":
            resp = requests.get(
                url=self.__url, params=self.__body, headers=self.__headers
            )
        elif self.__method == "POST":
            resp = requests.post(
                url=self.__url, params=self.__body, headers=self.__headers
            )
        else:
            raise ValueError(f"API Método nao valido {self.__method}.")

        print(resp)
        try:
            data = resp.json()
            self.__result = True
            self.__data = data
        except Exception as err:
            data = dict(
                error=str(err),
                result=False,
                response="exception",
                msg_cod=resp.status_code,
                msg_reason=resp.reason,
            )
            self.__data = data
            self.__respcode = resp.status_code
            self.__respstatus = resp.reason
            self.__result = False

        return data

    def execResp(self):
        """Realiza obtenção de mais dados do GET/POST no Servidor Informado"""
        return dict (
            conteudo = self.__data
            , http_code = self.__respcode
            , http_status = self.__respstatus
            , resultado = self.__result
        )