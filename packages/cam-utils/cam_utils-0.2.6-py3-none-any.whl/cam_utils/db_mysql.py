from mysql.connector import pooling
from mysql.connector import errors as mysql_errors

from cam_utils.valida_info import ValidaInfo

# class DBMariaDB <DBMySQL>:

class DBMySQL:
    """Classe de tratamento de conexão ao MySQL"""

    __libtag: str
    __last_query: str
    __last_insert_id: int
    __last_row_affected: int

    __registros = []
    __result: bool
    __resmsg: str
    __sucesso = bool

    __pool: object
    __connection: object
    __enderecoIP: str
    __dbname: str
    __port: int
    __username: str
    __password: str


    def __init__(self, ipaddress: str, port: int, dbname: str, user: str, secret: str):
        """Inicializa classe MySQL"""
        self.__libtag = "CAM_LIB_MYSQL :: "

        if not ValidaInfo().ipv4address(ipaddress):
            raise ValueError(f"{self.__libtag} Endereço IP nao valido {ipaddress}.")

        if not ValidaInfo().texto(dbname):
            raise ValueError(f"{self.__libtag} Database Name nao valido {dbname}.")
        
        if not ValidaInfo().texto(user):
            raise ValueError(f"{self.__libtag} Username nao valido {user}.")

        if not ValidaInfo().texto(secret):
            raise ValueError(f"{self.__libtag} Password nao valido {secret}.")

        if ValidaInfo().portaTCP(port):
            self.__port = port
        else:
            self.__port = 3306

        self.__username = user
        self.__password = secret
        self.__enderecoIP = ipaddress
        self.__dbname = dbname
        self.__result = False
        self.__sucesso = False
        try:
            db_config = {
                'host': self.__enderecoIP
                , 'user': self.__username
                , 'password': self.__password
                , 'database': self.__dbname
                , 'port': self.__port
            }

            self.__pool = pooling.MySQLConnectionPool(pool_name="cam_mysql_pool", pool_size=5, **db_config)
            cnx = self.connect()
            cnx.close() 
            self.__result = True

        except Exception as e:
            self.__result = False
            msgerror = str(e)
            self.__resmsg = f"{self.__libtag} Erro ao realizar conexão: {msgerror} - {self.__enderecoIP} - {self.__username}"
            print(self.__resmsg)


    def connect(self): 
        try:
            return self.__pool.get_connection()
        except mysql_errors.PoolError as e:
            self.__result = False
            msgerror = str(e)
            self.__resmsg = f"{self.__libtag} Erro ao realizar conexão: {msgerror} - {self.__enderecoIP} - {self.__username}"
            print(self.__resmsg)
            return None
        
    
    def query_fetch(self, query: str):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(query):
                raise ValueError(f"{self.__libtag} Query Não válido {query}.")

            self.__last_query = query
            cnx = self.connect()

            cursor = cnx.cursor(dictionary=True)
            cursor.execute(query)
    
            search_results = cursor.fetchall()
            qtdRegistros = len(search_results)
            if qtdRegistros > 0:
                self.__sucesso = True
            else:
                self.__sucesso = False
            self.__registros = search_results
            print(f"{self.__libtag} Consulta retornou {qtdRegistros} registros")

            return search_results
        
        except mysql_errors.PoolError as e:
            self.__result = False
            msgerror = str(e)
            self.__resmsg = f"{self.__libtag} Erro ao realizar conexão: {msgerror} - {self.__enderecoIP} - {self.__username}"
            print(self.__resmsg)
            return None


    def query_insert(self, query: str):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(query):
                raise ValueError(f"{self.__libtag} Insert query Não válido {query}.")

            self.__last_query = query
            cnx = self.connect()

            cursor = cnx.cursor(dictionary=True)

            # Executa a query de INSERT
            cursor.execute(query) 

            # Obtém o ID do último registro inserido
            self.__last_insert_id = cursor.lastrowid

            # Confirma a transação
            cnx.commit()

            # Fecha o cursor
            cursor.close()

            if self.__last_insert_id > 0:
                self.__sucesso = True
            else:
                self.__sucesso = False
                
            print(f"{self.__libtag} Insert criou registro {self.__last_insert_id}")
            
            return self.__last_insert_id
        
        except mysql_errors.PoolError as e:
            self.__result = False
            msgerror = str(e)
            self.__resmsg = f"{self.__libtag} Erro ao realizar conexão: {msgerror} - {self.__enderecoIP} - {self.__username}"
            print(self.__resmsg)
            return None


    def query_update(self, query: str):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(query):
                raise ValueError(f"{self.__libtag} UPDATE query Não válido {query}.")

            self.__last_query = query
            cnx = self.connect()

            cursor = cnx.cursor(dictionary=True)

            # Executa a query de UPDATE
            cursor.execute(query) 

            # Obtém o ID do último registro inserido
            self.__last_row_affected = cursor.rowcount

            # Confirma a transação
            cnx.commit()

            # Fecha o cursor
            cursor.close()

            if self.__last_insert_id > 0:
                self.__sucesso = True
            else:
                self.__sucesso = False
                
            print(f"{self.__libtag} UPDATE alterou {self.__last_insert_id} registros")
            
            return self.__last_insert_id
        
        except mysql_errors.PoolError as e:
            self.__result = False
            msgerror = str(e)
            self.__resmsg = f"{self.__libtag} Erro ao realizar conexão: {msgerror} - {self.__enderecoIP} - {self.__username}"
            print(self.__resmsg)
            return None


    def query_delete(self, query: str):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(query):
                raise ValueError(f"{self.__libtag} DELETE query Não válido {query}.")

            self.__last_query = query
            cnx = self.connect()

            cursor = cnx.cursor(dictionary=True)

            # Executa a query de UPDATE
            cursor.execute(query) 

            # Obtém o ID do último registro inserido
            self.__last_row_affected = cursor.rowcount

            # Confirma a transação
            cnx.commit()

            # Fecha o cursor
            cursor.close()

            if self.__last_insert_id > 0:
                self.__sucesso = True
            else:
                self.__sucesso = False
                
            print(f"{self.__libtag} DELETE alterou {self.__last_insert_id} registros")
            
            return self.__last_insert_id
        
        except mysql_errors.PoolError as e:
            self.__result = False
            msgerror = str(e)
            self.__resmsg = f"{self.__libtag} Erro ao realizar conexão: {msgerror} - {self.__enderecoIP} - {self.__username}"
            print(self.__resmsg)
            return None




    ## NAO USAR ESTA FUNCAO! 
    def __query_insert(self, table: str, data: object):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(table):
                raise ValueError(f"{self.__libtag} Insert Table Não válido {table}.")

            if len(data) < 1: 
                raise ValueError(f"{self.__libtag} Insert Data Não válido {data}.")
            
            columns = ', '.join(data.keys())
            values_template = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({values_template})"


            self.__last_query = query
            cnx = self.connect()

            cursor = cnx.cursor(dictionary=True)

            # Executa a query de INSERT
            cursor.execute(query, tuple(data.values()))

            # Obtém o ID do último registro inserido
            self.__last_insert_id = cursor.lastrowid

            # Confirma a transação
            cnx.commit()

            # Fecha o cursor
            cursor.close()

            if self.__last_insert_id > 0:
                self.__sucesso = True
            else:
                self.__sucesso = False
                
            print(f"{self.__libtag} Insert {table} criou registro {self.__last_insert_id}")
            
            return self.__last_insert_id
        
        except mysql_errors.PoolError as e:
            self.__result = False
            msgerror = str(e)
            self.__resmsg = f"{self.__libtag} Erro ao realizar conexão: {msgerror} - {self.__enderecoIP} - {self.__username}"
            print(self.__resmsg)
            return None


    def __query_update_data(self, key: str, valor: object):
            if valor is None: 
                return f" {key} = NULL "
            elif isinstance(valor, str):
                return f" {key}  = '{valor}' "
            elif isinstance(valor, int):
                return f" {key}  = {valor} "
            elif isinstance(valor, bool):
                return f" {key} = {valor} "
            else:
                return " "


    def __query_condition(self, condicao: str, valor: object):
            if valor is None: 
                return f" {condicao} IS NULL "
            elif isinstance(valor, str):
                return f" {condicao}  = '{valor}' "
            elif isinstance(valor, int):
                return f" {condicao}  = {valor} "
            elif isinstance(valor, bool):
                return f" {condicao} = {valor} "
            elif isinstance(valor, dict):
                query_condicao = " ( 1 = 0 "
                for condorkey, condorval in valor.items():
                    query_condicao += "OR " + self.__query_condition(condorkey, condorval)
                query_condicao += " ) "
                return query_condicao
            else:
                return " "

    ## NAO USAR ESTA FUNCAO! 
    def __query_update(self, table: str, data: dict, condicao: dict):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(table):
                raise ValueError(f"{self.__libtag} Update Table Não válido {table}.")

            if len(data) < 1: 
                raise ValueError(f"{self.__libtag} Update Data Não válido {data}.")
            
            if len(condicao) < 1: 
                query_condicao = "1 = 1"
            else: 
                query_condicao = "1 = 1"
                for condkey, condval in condicao.items():
                    query_condicao += " AND " + self.__query_condition(condkey, condval)
            

            for key, val in data.items():
                query_condicao += " AND " + self.__query_condition(condkey, condval)
            values_template = self.__query_update_data(data)
            
            query = f"UPDATE {table} SET {values_template} WHERE {query_condicao}"
            

            self.__last_query = query
            cnx = self.connect()

            cursor = cnx.cursor(dictionary=True)

            # Executa a query de INSERT
            cursor.execute(query, tuple(data.values()))

            # Obtém o ID do último registro inserido
            self.__last_insert_id = cursor.lastrowid

            # Confirma a transação
            cnx.commit()

            # Fecha o cursor
            cursor.close()

            if self.__last_insert_id > 0:
                self.__sucesso = True
            else:
                self.__sucesso = False
                
            print(f"{self.__libtag} Insert {table} criou registro {self.__last_insert_id}")
            
            return self.__last_insert_id
        
        except mysql_errors.PoolError as e:
            self.__result = False
            msgerror = str(e)
            self.__resmsg = f"{self.__libtag} Erro ao realizar conexão: {msgerror} - {self.__enderecoIP} - {self.__username}"
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
