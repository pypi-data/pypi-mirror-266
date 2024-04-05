import logging
import socket
import time
from typing import Any, Optional

from . import exceptions
from ._actions import actions_asterisk_13

logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [ %(levelname)s ] - %(message)s"
)


class AMI13:
    def __init__(
        self, server: str, username: str, password: str, port: int = 5038, timeout=5
    ):
        self.server = server
        self.username = username
        self.__password = password
        self.port = port
        self.__connection: Optional[socket.socket] = None
        self.timeout = timeout

    def __connect(self):
        self.__connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connection.settimeout(self.timeout)
        self.__connection.connect((self.server, self.port))
        return True

    def __disconnect(self) -> None:
        if self.__connection:
            self.__connection.close()

    def __login(self):
        cmd = {"Action": "Login", "Username": self.username, "Secret": self.__password}
        if not self.__connection:
            self.__connect()

        self.__connection.sendall(self.__cmd_parser(cmd))

        raw_response = ""
        while True:
            data = self.__connection.recv(4096)
            raw_response += data.decode()
            if "Response:" in raw_response:
                break

        response = {}
        lines = raw_response.splitlines()
        for line in lines:
            splitted = line.split(":", 1)
            if len(splitted) == 1 and splitted[0].startswith("Asterisk"):
                response["AMI"] = splitted[0]
            if len(splitted) == 2:
                key, value = splitted
                key = key.strip()
                if key == "Response":
                    response[key] = value.strip()
                if key == "Message":
                    response[key] = value.strip()

        if response.get("Response") == "Error":
            raise exceptions.AuthenticationError(response.get("Message"))

    def __logoff(self):
        cmd = {
            "Action": "Logoff",
        }
        if self.__connection:
            self.__connection.sendall(self.__cmd_parser(cmd))
            self.__disconnect()

    def __error_response(self, error: str, data: dict = {}) -> dict[str, Any]:
        logging.error(error)

        return {
            "success": False,
            "message": str(error),
            "data": data,
        }

    def __success_response(self, message: str, data: dict = {}) -> dict[str, Any]:
        logging.info(message)
        return {
            "success": True,
            "message": str(message),
            "data": data,
        }

    def __read_all(self, end_of_command: str) -> str:
        response = ""
        timeout = time.time() + self.timeout
        self.__connection.setblocking(False)  # Para evitar deadlock
        while True:
            if time.time() > timeout:
                raise TimeoutError("Timeout enquanto esperava resposta do comando.")
            try:
                data = self.__connection.recv(4096)
                if data:
                    response += data.decode()
                    if end_of_command in response:
                        break
            except BlockingIOError:
                time.sleep(0.1)
            except Exception as e:
                logging.error(e)
                raise e
        self.__connection.setblocking(True)  # Reabilitar para uso do sendall
        return response

    def cmd(self, cmd: str) -> dict[str, Any]:
        try:
            _cmd = {
                "Action": "Command",
                "Command": cmd,
            }

            if not self.__connection:
                self.__connect()
                self.__login()

            if self.__connection:
                self.__connection.sendall(self.__cmd_parser(_cmd))

            response = self.__read_all("--END COMMAND--")
            return self.__success_response(f"Command: {cmd}", {"response": response})
        except Exception as e:
            return self.__error_response(str(e))

    def __build_sip_peers(self, data: str) -> dict[str, Any]:
        fields = (
            "Channeltype"
            "ObjectName"
            "ChanObjectType"
            "IPaddress"
            "IPport"
            "Dynamic"
            "AutoForcerport"
            "Forcerport"
            "AutoComedia"
            "Comedia"
            "VideoSupport"
            "TextSupport"
            "ACL"
            "Status"
            "RealtimeDevice"
            "Description"
            "Accountcode"
        )

        item = {}
        _data = {}
        lines = data.splitlines()
        for line in lines:
            splitted = line.split(":", 1)
            if len(splitted) == 2:
                key, value = splitted
                key = key.strip()
                if key in fields:
                    item[key] = value.strip()
                    if key == "Accountcode":
                        _data[item["ObjectName"]] = item
                        item = {}
        return _data

    def sip_peers(self) -> dict:
        try:
            cmd = {
                "Action": "SIPpeers",
            }
            self.__login()
            self.__connection.sendall(self.__cmd_parser(cmd))  # type: ignore
            response = self.__read_all("PeerlistComplete")
            data = self.__build_sip_peers(response)
            return self.__success_response("SIP Peers", data)
        except Exception as e:
            return self.__error_response(str(e))

    def __parse_error(self, data: str) -> dict[str, str]:
        _list_data = data.splitlines()
        result = {}
        has_erro = False
        for line in _list_data:
            if "Response: Error" in line:
                has_erro = True
            if has_erro and "Message:" in line:
                result["AMIStatus"] = "Error"
                result["Message"] = line.split(":")[1].strip()

        return result

    def __parse_sip_peer(self, data: str) -> dict[str, str]:
        fields = (
            "Channeltype",
            "ObjectName",
            "ChanObjectType",
            "SecretExist",
            "RemoteSecretExist",
            "MD5SecretExist",
            "Context",
            "Language",
            "ToneZone",
            "AMAflags",
            "CID-CallingPres",
            "Callgroup",
            "Pickupgroup",
            "Named Callgroup",
            "Named Pickupgroup",
            "MOHSuggest",
            "VoiceMailbox",
            "TransferMode",
            "LastMsgsSent",
            "Maxforwards",
            "Call-limit",
            "Busy-level",
            "MaxCallBR",
            "Dynamic",
            "Callerid",
            "RegExpire",
            "SIP-AuthInsecure",
            "SIP-Forcerport",
            "SIP-Comedia",
            "ACL",
            "SIP-CanReinvite",
            "SIP-DirectMedia",
            "SIP-PromiscRedir",
            "SIP-UserPhone",
            "SIP-VideoSupport",
            "SIP-TextSupport",
            "SIP-T.38Support",
            "SIP-T.38EC",
            "SIP-T.38MaxDtgrm",
            "SIP-Sess-Timers",
            "SIP-Sess-Refresh",
            "SIP-Sess-Expires",
            "SIP-Sess-Min",
            "SIP-RTP-Engine",
            "SIP-Encryption",
            "SIP-RTCP-Mux",
            "SIP-DTMFmode",
            "ToHost",
            "Address-IP",
            "Address-Port",
            "Default-addr-IP",
            "Default-addr-port",
            "Default-Username",
            "Codecs",
            "Status",
            "SIP-Useragent",
            "Reg-Contact",
            "QualifyFreq",
            "Parkinglot",
            "SIP-Use-Reason-Header",
            "Description",
        )

        _data = {"AMIStatus": "Success"}
        lines = data.splitlines()
        for line in lines:
            splitted = line.split(":", 1)
            if len(splitted) == 2:
                key, value = splitted
                key = key.strip()
                if key in fields:
                    _data[key] = value.strip()
        return _data

    def sip_peer(self, peer: str) -> dict[str, str]:
        try:
            cmd = {
                "Action": "SIPshowpeer",
                "Peer": peer,
            }

            if not self.__connection:
                self.__connect()
                self.__login()

            if self.__connection:
                self.__connection.sendall(self.__cmd_parser(cmd))

            response = ""
            while True:
                data = self.__connection.recv(4096)
                response += data.decode()
                if "Description: \r\n\r\n" in response:
                    break
                if "Response: Error" in response:
                    return self.__parse_error(response)
            data = self.__parse_sip_peer(response)
            return self.__success_response(f"SIP Peer {peer}", data)
        except Exception as e:
            return self.__error_response(str(e))

    def __cmd_parser(self, cmd: dict[str, str]) -> bytes:
        if cmd.get("Action") not in actions_asterisk_13:
            raise exceptions.WrongAMIAction(
                f"The action {cmd.get('Action')} is not supported"
            )

        _cmd = ""
        for key, value in cmd.items():
            _cmd += f"{key}: {value}\r\n"
        _cmd += "\r\n"

        return _cmd.encode()
