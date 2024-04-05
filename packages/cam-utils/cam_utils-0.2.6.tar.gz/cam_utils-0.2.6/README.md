# biblioteca cam_utils

Bem vindo a 1a biblioteca Python3 da CAM Tecnologia para ser incorporada e reutilizada nos projetos de desenvolvimento Pyhton. 
A biblioteca `cam_utils` na versão atual foi desenvolvida para Python 3 e armazenada livremente no PyPI:

```markdown

# cam_utils

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cam-utils)
![PyPI](https://img.shields.io/pypi/v/cam-utils)
![PyPI - Downloads](https://img.shields.io/pypi/dm/cam-utils)
![PyPI - License](https://img.shields.io/pypi/l/cam-utils)


## Instalação

Você pode instalar `cam_utils` via pip:

```bash
pip install cam-utils
```



## Operações disponíveis na biblioteca

**cam_utils** é uma biblioteca Python 3 que fornece utilitários seguintes operações:

- **Configurações:** (settings) Disponibilizar acesso a classe de configuração via environment
- **LDAP:** (db_ldap) Disponibilizar acesso a classe de leitura e escrita no LDAP
- **ElasticSearch:** (db_elasticsearch) Disponibilizar acesso a classe de leitura e escrita no ElasticSearch
- **Validação:** (valida_info) Disponibilizar métodos/funções de validação de dados 
- **Request API:** (api_request) Disponibilizar métodos/funções de Requisição HTTP/HTTPS a API
- **RabbitMQ:** (db_rabbitmq) Disponibilizar métodos/funções de Consumo (contínuo ou instantâneo) e publicação no RabbitMQ

## Recursos

DOCUMENTAR!!

## Uso

```python
from cam_utils.valida_info import ValidaInfo

# Exemplo de Validaçaõ de Informação 
cep = '20765-000' 
if ValidaInfo().zipcodeBR(cep):
    print(f"CEP Válido: {cep}")
else:
    print(f"CEP Inválido: {cep}")

# Documentar outros exemplos

```


## Contribuição

Contribuições são bem-vindas! Se você encontrar um bug ou tiver uma ideia para uma nova funcionalidade, sinta-se à vontade para abrir uma [issue](https://repo.camvoip.com.br/engenharia/bibliotecas-cam/python/cam_utils/issues) ou enviar um [pull request](https://repo.camvoip.com.br/engenharia/bibliotecas-cam/python/cam_utils/pulls).


## Licença

Este projeto é licenciado sob os termos da Licença MIT. Consulte o arquivo [LICENSE](LICENSE) para obter mais detalhes.


## Project status

A DOCUMENTAR
