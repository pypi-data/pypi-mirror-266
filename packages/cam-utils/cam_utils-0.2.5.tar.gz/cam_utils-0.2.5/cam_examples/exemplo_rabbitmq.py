# CODIGO SANIC PARA Automação de Endpoints

from lib.settings import rabbitmq_settings

from lib.db_rabbitmq import DBRabbitMQ

from pika.spec import Basic
from pika.spec import BasicProperties


def consolidador_consume_callback_continuo(
    rabbitdb: DBRabbitMQ,
    method_frame: Basic.Deliver,
    header_frame: BasicProperties,
    body: bytes,
):
    print("Consolidador Callback Start")
    print(body)
    print("Consolidador Callback End")


def consolidador_consume_callback_instantaneo(
    rabbitdb: DBRabbitMQ,
    method_frame: Basic.Deliver,
    header_frame: BasicProperties,
    body: bytes,
):
    print("Consolidador Callback Start")
    print(body)
    rabbitdb.stopConsuming()
    print("Consolidador Callback End")


def consolidador_continuo(resultConfig):

    respjson = dict(sucesso=False, msg="")

    print("consolidador_main Start")

    #### MAIN CODIGO Consolidacao
    """
    #### Inicializado a Comunicacao com RabbitMQ
    #### Abro o consumo 
    #### Abro o callback 
            ### Faco a consulta ao ElasticSerch
            #### INSERIR O CODIGO CONSOLIDACAO AQUI
    ### RETORNO a Publicacao 
    """

    # Inicializa classe RabbitMQ
    rabbitdb = DBRabbitMQ(
        rabbitmq_settings.HOST,
        rabbitmq_settings.PORT,
        rabbitmq_settings.USER,
        rabbitmq_settings.PASSWORD,
        rabbitmq_settings.VIRTUAL,
    )

    # Inicializa Consumo
    rabbitdb.consume(rabbitmq_settings.QUEUE_CONSUME)
    rabbitdb.callback(consolidador_consume_callback_continuo)

    try:
        rabbitdb.startConsuming()
    except Exception as e:
        print(f"Error in consumer: {e}")
    finally:
        rabbitdb.close()

    print("consolidador_main Inicializado")

    return respjson


def consolidador_instantaneo(resultConfig):

    respjson = dict(sucesso=False, msg="")

    print("consolidador_main Start")

    #### MAIN CODIGO Consolidacao
    """
    #### Inicializado a Comunicacao com RabbitMQ
    #### Abro o consumo 
    #### Abro o callback 
            ### Faco a consulta ao ElasticSerch
            #### INSERIR O CODIGO CONSOLIDACAO AQUI
    ### RETORNO a Publicacao 
    """

    # Inicializa classe RabbitMQ
    rabbitdb = DBRabbitMQ(
        rabbitmq_settings.HOST,
        rabbitmq_settings.PORT,
        rabbitmq_settings.USER,
        rabbitmq_settings.PASSWORD,
        rabbitmq_settings.VIRTUAL,
    )

    # Inicializa Consumo
    rabbitdb.consume(rabbitmq_settings.QUEUE_CONSUME)
    rabbitdb.callback(consolidador_consume_callback_instantaneo)

    try:
        rabbitdb.startConsuming()
    except Exception as e:
        print(f"Error in consumer: {e}")
    finally:
        rabbitdb.close()

    print("consolidador_main Inicializado")

    return respjson
