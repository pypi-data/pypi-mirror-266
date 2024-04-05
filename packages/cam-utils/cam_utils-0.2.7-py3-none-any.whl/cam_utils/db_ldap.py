import ldap
from cam_utils.valida_info import ValidaInfo

# from ldap import LDAPObject


class DBLdap:
    """Classe de tratamento de conexão ao LDAP"""

    __libtag: str
    __search_filter: str
    __base_dn: str

    __registros = []
    __result: bool
    __resmsg: str
    __sucesso = bool

    __connection: object
    __enderecoIP: str
    __scheme: str
    __port: int
    __username: str
    __password: str

    def __init__(self, ipaddress: str, port: int, scheme: bool, user: str, secret: str):
        """Inicializa classe LDAP"""
        self.__libtag = "CAM_LIB_LDAP :: "

        if not ValidaInfo().ipv4address(ipaddress):
            raise ValueError(f"{self.__libtag} Endereço IP nao valido {ipaddress}.")

        if ValidaInfo().texto(user):
            raise ValueError(f"{self.__libtag} Username nao valido {user}.")

        if ValidaInfo().texto(secret):
            raise ValueError(f"{self.__libtag} Password nao valido {secret}.")

        if scheme:
            self.__scheme = "ldaps"
        else:
            self.__scheme = "ldap"

        if ValidaInfo().portaTCP(port):
            self.__port = port
        else:
            self.__port = 389

        self.__username = user
        self.__password = secret
        self.__enderecoIP = ipaddress
        self.__result = False
        self.__sucesso = False
        try:
            initldap = f"{self.__scheme}://{self.__enderecoIP}:{self.__port}"
            print(f"{self.__libtag} Inicializando {initldap}")
            self.__connection = ldap.initialize(initldap)
            print(f"{self.__libtag} Logando {self.__username}")
            self.__connection.simple_bind_s(self.__username, self.__password)
            print(f"{self.__libtag} Conexão com sucesso {initldap}")
            self.__result = True
        except ldap.LDAPError as e:
            ldape = str(e)
            self.__resmsg = f"{self.__libtag} Erro ao realizar conexão: {ldape} - {self.__enderecoIP} - {self.__username}"
            print(self.__resmsg)

    def search_dn_objects(self, base_dn, search_filter):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(base_dn):
                raise ValueError(f"{self.__libtag} BASE DN Não válido {base_dn}.")

            self.__search_filter = search_filter
            self.__base_dn = base_dn
            search_results = self.__connection.search_s(
                base_dn, ldap.SCOPE_SUBTREE, search_filter
            )
            qtdRegistros = len(search_results)
            if qtdRegistros > 0:
                self.__sucesso = True
            else:
                self.__sucesso = False
            self.__registros = search_results
            print(f"{self.__libtag} Consulta retornou {qtdRegistros} registros")
            return search_results
        except ldap.LDAPError as e:
            ldape = str(e)
            self.__resmsg = f"{self.__libtag} Busca Error: {ldape} {self.__base_dn} {self.__search_filter}"
            print(self.__resmsg)
            return None

    def search_resultado(self):
        return self.__sucesso

    def search_registros(self):
        return self.__registros

    def getStatusConnection(self):
        return self.__result

    def getError(self):
        return self.__resmsg
