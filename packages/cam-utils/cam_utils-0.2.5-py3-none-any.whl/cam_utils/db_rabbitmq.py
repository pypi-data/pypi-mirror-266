import functools
import json

from cam_utils.valida_info import ValidaInfo
from pika import (
    BasicProperties,
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic


class DBRabbitMQ:
    """Classe de tratamento de conexão ao RabbitMQ"""

    """
        Inicialização: Abro a conexão
        Publicação: Inicializo o canal e publico e encerro o canal 
        ConsumoInstantaneo: preciso receber a funcao de callback, queue 
        ConsumoContinuo: preciso receber a funcao de callback, queue 
    """
    __libtag: str

    """ Conexao """
    __ipaddress: str
    __port: int
    __virtualhost: str
    __username: str
    __password: str

    """ Conexão """
    __connection: object
    __channel: BlockingChannel
    __queues: list

    """ INDEX """
    __queueConsume: str
    __queuePublish: str
    callbackFunc: any

    """ Resultado de conexão """
    __result: bool
    __resmsg: str

    """ Resultado de pesquisa """
    __registros: list
    __sucesso: bool

    def __init__(self, host: str, port: str, user: str, secret: str, virtual: str):
        """Inicializa classe RABBITMQ"""
        self.__libtag = "CAM_LIB_RABBITMQ :: "

        print(f"{self.__libtag} Inicializando")

        if ValidaInfo().ipv4address(host):
            self.__ipaddress = host
        elif ValidaInfo().texto(host):
            self.__ipaddress = host
        else:
            raise ValueError(
                f"{self.__libtag} Endereço Informado não é hostname ou endereço IP  {host}."
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

        if not ValidaInfo().texto(virtual):
            raise ValueError(f"{self.__libtag} Virtual Host nao valido {virtual}.")

        self.__username = user
        self.__password = secret
        self.__virtualhost = virtual
        self.__result = False
        self.__sucesso = False
        self.__queueConsume = None
        self.__queuePublish = None
        self.__queues = []
        self.__channel = None
        try:
            print(f"{self.__libtag} Conectando {self.__ipaddress}")
            self.__connection = BlockingConnection(
                ConnectionParameters(
                    host=self.__ipaddress,
                    port=self.__port,
                    virtual_host=self.__virtualhost,
                    credentials=PlainCredentials(
                        username=self.__username,
                        password=self.__password,
                    ),
                )
            )
            self.__result = self.test()

            self.__channel = self.__connection.channel()

            print(f"{self.__libtag} Conectado {self.__result}")
        except Exception as e:
            err = str(e)
            self.__resmsg = f"{self.__libtag} Erro ao realizar conexão: {err} - {self.__ipaddress} - {self.__port} - {self.__username} - {self.__virtualhost}"
            print(self.__resmsg)

    def callback(self, callfunction: any):
        if callfunction is None:
            raise ValueError(f"{self.__libtag} callback nao valido {callfunction}.")

        self.callbackFunc = callfunction

    def close(self):
        return self.__connection.close()

    def isOpen(self):
        print(f"{self.__libtag} Checando status da conexao {self.__connection}")
        if self.__connection:
            return True
        else:
            return False

    def test(self):
        if self.__connection:
            return True
        else:
            return False

    def isOpenChan(self):
        print(f"{self.__libtag} Checando status do canal")
        if self.__channel:
            return True
        else:
            return False

    def __openChan(self, queue: str):
        try:
            self.__resmsg = ""

            if not ValidaInfo().texto(queue):
                raise ValueError(f"{self.__libtag} QUEUE NAME Não válido {queue}.")

            self.__queuePublish = queue

            if not self.isOpen():
                raise ValueError(f"{self.__libtag} Conexão Encerrada.")

            if not self.__channel:
                self.__channel = self.__connection.channel()

            self.__channel.queue_declare(self.__queuePublish, durable=True)

            if not ValidaInfo().searchInArray(self.__queues, queue):
                self.__queues.append(queue)

            return self.isOpenChan()

        except Exception as e:
            err = str(e)
            self.__resmsg = f"{self.__libtag} Open Chan error: {err} {queue}"
            print(self.__resmsg)
            return False

    def openChanConsume(self, queue: str):
        res = self.__openChan(queue)
        if res:
            self.__queueConsume = queue
        else:
            self.__queueConsume = None
        return res

    def openChanPublish(self, queue: str):
        res = self.__openChan(queue)
        if res:
            self.__queuePublish = queue
        else:
            self.__queuePublish = None
        return res

    def publish(self, queue: str, info: json):
        try:
            self.__resmsg = ""

            print(f"{self.__libtag} Publish - Validando queue {queue}")
            if not ValidaInfo().texto(queue):
                raise ValueError(f"{self.__libtag} QUEUE NAME Não válido {queue}.")

            if not self.isOpen():
                raise ValueError(f"{self.__libtag} Conexão Encerrada.")

            print(
                f"{self.__libtag} Publish - Validando processo  Abrindo Canal {queue}"
            )

            if self.__queuePublish != queue:
                self.openChanPublish(queue)

            if not self.isOpenChan():
                self.openChanPublish(queue)
                if not self.isOpenChan():
                    raise ValueError(
                        f"{self.__libtag} Chan Publish Não foi aberto {queue}."
                    )

            print(f"{self.__libtag} Publish - Msg {queue}")
            propertiesPublish = BasicProperties(delivery_mode=2)
            self.__channel.basic_publish(
                exchange="",
                routing_key=self.__queuePublish,
                body=info,
                properties=propertiesPublish,
            )

            return True
        except Exception as e:
            err = str(e)
            self.__resmsg = f"{self.__libtag} Publish Error: {err} {queue}"
            print(self.__resmsg)
            return False

    def consume(self, queue: str):
        try:
            self.__resmsg = ""

            print(f"{self.__libtag} Consumo - Validando queue {queue}")

            if not ValidaInfo().texto(queue):
                raise ValueError(f"{self.__libtag} QUEUE NAME Não válido {queue}.")

            if not self.isOpen():
                raise ValueError(f"{self.__libtag} Conexão Encerrada.")

            print(
                f"{self.__libtag} Consumo - Validando processo  Abrindo Canal {queue}"
            )

            if self.__queueConsume != queue:
                print(
                    f"{self.__libtag} Consumo - Fila nao definida - Abrindo Canal {queue}"
                )
                self.openChanConsume(queue)

            if not self.isOpenChan():
                self.openChanConsume(queue)
                if not self.isOpenChan():
                    raise ValueError(
                        f"{self.__libtag} Chan Consumo Não foi aberto {queue}."
                    )

            print(f"{self.__libtag} Consumo - definindo CallBack {queue}")

            # basic_consume(queue, on_message_callback, auto_ack=False, exclusive=False, consumer_tag=None, arguments=None)[source]
            # channel.basic_consume(collector_queue, on_message)
            # channel.basic_consume(queue='input_queue', on_message_callback=callback, auto_ack=True)

            # Create a partial function with extra argument
            partial_callback = functools.partial(callbackConsume, rabbitMQ=self)

            print(f"{self.__libtag} Consumo - realizando Consumo {queue}")
            self.__channel.basic_consume(
                queue=self.__queueConsume,
                on_message_callback=partial_callback,
                auto_ack=False,
                exclusive=False,
                consumer_tag=None,
            )

            print(f"{self.__libtag} Consumo - criado {queue}")

            return True
        except Exception as e:
            err = str(e)
            self.__resmsg = f"{self.__libtag} Consume Error: {err} {queue}"
            print(self.__resmsg)
            return False

    def getChannel(self):
        return self.__channel

    def startConsuming(self):
        return self.__channel.start_consuming()

    def stopConsuming(self):
        return self.__channel.stop_consuming()

    def consumeACK(self, tag: int):
        try:
            self.__channel.basic_ack(delivery_tag=tag)
            return True
        except Exception as e:
            err = str(e)
            self.__resmsg = f"{self.__libtag} Consume Ack Error: {err} {tag}"
            print(self.__resmsg)
            return False


def callbackConsume(
    channel: BlockingChannel,
    method_frame: Basic.Deliver,
    header_frame: BasicProperties,
    body: bytes,
    rabbitMQ: DBRabbitMQ,
):
    try:
        print("Start CallBackConsume")
        print(method_frame.delivery_tag)
        print(method_frame.consumer_tag)
        print(body)
        print(rabbitMQ.getChannel())
        rabbitMQ.callbackFunc(rabbitMQ, method_frame, header_frame, body)
        rabbitMQ.consumeACK(method_frame.delivery_tag)
    except Exception as e:
        print("Error CallBackConsume")
        print(e)
