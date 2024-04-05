# CODIGO SANIC PARA Automação de Endpoints

from lib.settings import es_settings

from lib.db_elasticsearch import DBElasticSearch


def elastic_consulta(resultLogin):

    respjson = dict(sucesso=False, msg="")

    """
- [ ] elastic_server = 'https://estatisticas-api.fone.rnp.br' # Elasticsearch URL Access
- [ ] elastic_port = '443'  # Elasticsearch port 
- [ ] elastic_secret = 'your_password' # Elastichsearch secret 
- [ ] elastic_user = 'your_user'  # Elasticsearch user with w/r index_name access
- [ ] elastic_index = 'index_name'  # Elasticsearch index 
    """

    print("elastic_consulta Start")

    #### MAIN CODIGO CONSULTA ElasticSearch
    try:

        # Inicializa classe ElasticSearch
        db = DBElasticSearch(
            es_settings.HOST,
            es_settings.PORT,
            es_settings.USER,
            es_settings.PASSWORD,
            es_settings.SCHEME,
        )

        print("elastic_consulta Inicializado")

        if not db.ping():
            raise ValueError(f"Elastic_Consulta indisponivel {es_settings.HOST}.")

        print("elastic_consulta Conectado")
        print(db.info())

        # Consulta # Search DN
        query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": [
                        {"match_all": {}},
                        {
                            "range": {
                                "setupTimeHR": {
                                    "gte": "2024-02-04T02:27:06.982Z",
                                    "lte": "2024-03-05T02:27:06.982Z",
                                    "format": "strict_date_optional_time",
                                }
                            }
                        },
                    ],
                    "should": [],
                    "must_not": [],
                }
            }
        }
        objects = db.search_document(es_settings.INDEX, query)

        print(objects["hits"]["hits"])

        for doc in objects["hits"]["hits"]:
            print(doc["_id"])
            print(doc["_source"])

        numregs = len(objects)

        # Realiza Search da Pesquisa
        # print(objects)
        respjson["sucesso"] = True
        respjson["msgcol"] = f"Registros localizados COL-*: {numregs}"

    except Exception as err:
        # print(err)
        respjson["msg"] = str(err)
        respjson["sucesso"] = False

    return respjson
