import re


class ValidaInfo:
    """Classe de validação de Campos"""

    def texto(self, input):
        """Valida se string é vazia"""
        if len(input) > 0:
            return True
        else:
            return False

    def numeric(self, numstring):
        """Valida se string informada é numerica"""
        return numstring.isnumeric()

    def portaTCP(self, numstring):
        """Valida se string informada é numerica e está válida numa porta TCP"""
        if not numstring.isnumeric():
            return False
        else:
            numport = int(numstring)
            if numport < 1 or numport > 65534:
                return False
            else:
                return True

    def keyExists(self, aurelio: dict, palavra: str):
        return palavra in aurelio

    def is_list(self, lista):
        return isinstance(lista, list)

    def searchInArray(self, lista, elemento: str):
        if not self.is_list(lista):
            return False

        for item in lista:
            if item == elemento:
                return True

        return False

    def onlynumbers(self, numstring):
        """Valida se String só possui numeros"""
        site_expression = "^\\d+$"

        match = re.match(site_expression, numstring)
        if not match:
            return False
        else:
            return True

    def url(self, urlstring):
        """Valida se URL informada atende a expressão regular"""
        site_expression = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
        match = re.match(site_expression, urlstring)
        if not match:
            return False
        else:
            return True

    def zipcodeBR(self, cep):
        """Valida se CEP está no padrão BR"""
        expression = "^[0-9]{5}(?:-?([0-9]{3}))?$"
        match = re.match(expression, cep)
        if not match:
            return False
        else:
            return True

    def uuid(self, struuid):
        """Valida se UUID está no padrão regular"""
        expression = (
            "^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )
        match = re.match(expression, struuid)
        if not match:
            return False
        else:
            return True

    def e164(self, strphone):
        """Valida se Número telefonico está no padrão E.164 '+552131891050'"""
        expression = "^\\+?[1-9][0-9]{7,14}$"

        match = re.match(expression, strphone)
        if not match:
            return False
        else:
            return True

    def telefoneBR(self, strphone):
        """Valida se Número telefonico está no padrão BR '(21) 3189-1050'"""
        expression = "^(\(?([0-9]{2})\)?)?[-.\ ]?([0-9]{4,5})[-.\ ]?([0-9]{4})$"

        match = re.match(expression, strphone)
        if not match:
            return False
        else:
            return True

    def macaddress(self, mac):
        """Valida se MAC está no padrão IEEE 802"""
        expression = "^(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})$"

        match = re.match(expression, mac)
        if not match:
            return False
        else:
            return True

    def ipv4address(self, ip):
        """Valida se Endereço IPv4 é válido"""
        expression = "^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"

        match = re.match(expression, ip)
        if not match:
            return False
        else:
            return True

    def ipaddress(self, ip):
        return self.ipv4address(ip)

    def emailaddress(self, email):
        """Valida se E-mail está no padrão RFC 5322"""
        expression = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])"

        match = re.match(expression, email)
        if not match:
            return False
        else:
            return True

    def dateBR(self, date):
        """Valida se Data está no padrão BR - DD/MM/YYYY"""
        expression = "^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}$"

        match = re.match(expression, date)
        if not match:
            return False
        else:
            return True

    def dateISO8061(self, date):
        """Valida se Data está no padrão ISO 8061 - 2021-11-04T22:32:47.142354-10:00"""
        expression = "^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}$"

        match = re.match(expression, date)
        if not match:
            return False
        else:
            return True
