import datetime

# from lib.requestAPI import requestAPI
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk, scan
from cam_utils.valida_info import ValidaInfo


# Define the generator function to prepare documents in bulk format
def generate_actions(documents, indexname):
    for doc in documents:
        yield {"_index": indexname, "_id": doc["id"], "_source": doc}


class DBElasticSearch:
    """Classe de tratamento de conexão ao ELASTICSEARCH"""

    """
        - [ ] elastic_server = 'https://estatisticas-db.fone.rnp.br' # Elasticsearch URL Access
        - [ ] elastic_port = '443'  # Elasticsearch port 
        - [ ] elastic_secret = 'your_password' # Elastichsearch secret 
        - [ ] elastic_user = 'your_user'  # Elasticsearch user with w/r index_name access
    """
    __libtag: str

    """ Conexao """
    __url: str
    __port: int
    __username: str
    __password: str
    __scheme: str
    __connection: object
    """ INDEX """
    __indexname: str
    """ Resultado de conexão """
    __result: bool
    __resmsg: str
    """ Resultado de pesquisa """
    __registros = []
    __sucesso = bool

    def __init__(self, url: str, port: str, user: str, secret: str, security: str):
        """Inicializa classe ELASTICSEARCH"""
        self.__libtag = "CAM_LIB_ELASTICSEARCH :: "

        print(f"{self.__libtag} Inicializando")

        if security == "https":
            self.__scheme = "https"
        else:
            self.__scheme = "http"

        if ValidaInfo().url(url):
            self.__url = url
        elif ValidaInfo().ipv4address(url):
            self.__url = url
        else:
            raise ValueError(
                f"{self.__libtag} Endereço Informado não é URL ou endereço IP  {url}."
            )

        if port is None or port == "" or port == "0":
            self.__port = 0
        elif ValidaInfo().portaTCP(port):
            self.__port = int(port)
        else:
            raise ValueError(f"{self.__libtag} Porta TCP nao válida {user}.")

        if not ValidaInfo().texto(user):
            raise ValueError(f"{self.__libtag} Username nao valido {user}.")

        if not ValidaInfo().texto(secret):
            raise ValueError(f"{self.__libtag} Password nao valido {secret}.")

        self.__username = user
        self.__password = secret
        self.__result = False
        self.__sucesso = False
        try:
            print(f"{self.__libtag} Conectando {self.__url}")
            if self.__scheme == "http":
                self.__connection = Elasticsearch(
                    self.__url, http_auth=(self.__username, self.__password)
                )
            else:
                self.__connection = Elasticsearch(
                    self.__url,
                    connection_class=RequestsHttpConnection,
                    http_auth=(self.__username, self.__password),
                    use_ssl=True,
                    verify_certs=False,
                    ssl_show_warn=False,
                )

            self.__result = self.ping()

            print(f"{self.__libtag} Conectado {self.__result}")
        except Exception as e:
            err = str(e)
            self.__resmsg = f"{self.__libtag} Erro ao realizar conexão: {err} - {self.__url} - {self.__port} - {self.__username} - {self.__scheme}"
            print(self.__resmsg)

    def info(self):
        return self.__connection.info()

    def ping(self):
        return self.__connection.ping()

    def update_alldocuments(self, indexname, update_field, new_value):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(indexname):
                raise ValueError(f"{self.__libtag} INDEX NAME Não válido {indexname}.")

            self.__indexname = indexname

            if not ValidaInfo().texto(update_field):
                raise ValueError(f"{self.__libtag} FIELD Não válido {update_field}.")

            if not self.ping():
                raise ValueError(f"{self.__libtag} PING inacessível.")

            # Use scan API to retrieve all documents in the index
            documents = scan(
                self.__connection, index=indexname, query={"query": {"match_all": {}}}
            )

            count = 0

            # Update documents with the specified keyword value
            for doc in documents:
                doc_id = doc["_id"]
                doc_source = doc["_source"]
                doc_source[update_field] = new_value
                doc_source["dtAtualizado"] = datetime.datetime.now()
                self.__connection.index(indexname, id=doc_id, body=doc_source)
                count = count + 1

            print(f"{self.__libtag} {count} Documentos atualizados com sucesso")

            return count
        except Exception as e:
            err = str(e)
            self.__resmsg = f"{self.__libtag} Update index error: {err} {self.__indexname} {update_field}"
            print(self.__resmsg)
            return 0

    def write_document(self, indexname: str, doc_id: str, doc_body: dict):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(indexname):
                raise ValueError(f"{self.__libtag} INDEX NAME Não válido {indexname}.")

            self.__indexname = indexname

            if not ValidaInfo().texto(doc_id):
                raise ValueError(f"{self.__libtag} DOC ID Não válido {doc_id}.")

            if not self.ping():
                raise ValueError(f"{self.__libtag} PING inacessível.")

            # Index a new document or update an existing document
            self.__connection.index(index=indexname, id=doc_id, body=doc_body)

            print(f"{self.__libtag} {doc_id} Inserido com sucesso")

            return True
        except Exception as e:
            err = str(e)
            self.__resmsg = (
                f"{self.__libtag} INSERT index error: {err} {indexname} {doc_id}"
            )
            print(self.__resmsg)
            return False

    def get_document(self, indexname: str, doc_id: str):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(indexname):
                raise ValueError(f"{self.__libtag} INDEX NAME Não válido {indexname}.")

            self.__indexname = indexname

            if not ValidaInfo().texto(doc_id):
                raise ValueError(f"{self.__libtag} DOC ID Não válido {doc_id}.")

            if not self.ping():
                raise ValueError(f"{self.__libtag} PING inacessível.")

            # Retrieve document by ID
            document = self.__connection.get(index=indexname, id=doc_id)
            print(f"{self.__libtag} {doc_id} Identificado com sucesso")

            return document["_source"]

        except Exception as e:
            err = str(e)
            self.__resmsg = (
                f"{self.__libtag} GetDocument index error: {err} {indexname} {doc_id}"
            )
            print(self.__resmsg)
            return None

    def search_document(self, indexname: str, query: dict):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(indexname):
                raise ValueError(f"{self.__libtag} INDEX NAME Não válido {indexname}.")

            self.__indexname = indexname

            if not ValidaInfo().keyExists(query, "query"):
                raise ValueError(f"{self.__libtag} Query Não localizado {str(query)}.")

            if not self.ping():
                raise ValueError(f"{self.__libtag} PING inacessível.")

            # Search documents based on the query
            search_results = self.__connection.search(index=indexname, body=query)
            return search_results

        except Exception as e:
            err = str(e)
            self.__resmsg = f"{self.__libtag} SearchDocument index error: {err} {indexname} {str(query)}"
            print(self.__resmsg)
            return None

    def delete_document(self, indexname: str, query: dict):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(indexname):
                raise ValueError(f"{self.__libtag} INDEX NAME Não válido {indexname}.")

            self.__indexname = indexname

            if not ValidaInfo().keyExists(query, "query"):
                raise ValueError(f"{self.__libtag} Query Não localizado {str(query)}.")

            if not self.ping():
                raise ValueError(f"{self.__libtag} PING inacessível.")

            # Search documents based on the query
            deleteResult = self.__connection.delete_by_query(
                index=indexname, body=query
            )
            return deleteResult

        except Exception as e:
            err = str(e)
            self.__resmsg = f"{self.__libtag} DeleteDocument index error: {err} {indexname} {str(query)}"
            print(self.__resmsg)
            return None

    def bulk_documents(self, indexname: str, documents):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(indexname):
                raise ValueError(f"{self.__libtag} INDEX NAME Não válido {indexname}.")

            self.__indexname = indexname

            if not ValidaInfo().is_list(documents):
                raise ValueError(
                    f"{self.__libtag} DOCUMENTS Não é Lista :: Registros: {len(documents)}."
                )

            if not self.ping():
                raise ValueError(f"{self.__libtag} PING inacessível.")

            # Index a new document or update an existing document
            result = bulk(self.__connection, generate_actions(documents, indexname))

            print(f"{self.__libtag} {result} Inserido com sucesso")

            return True
        except Exception as e:
            err = str(e)
            self.__resmsg = f"{self.__libtag} INSERT index error: {err} {indexname} {len(documents)}"
            print(self.__resmsg)
            return False
