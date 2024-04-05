from unittest.mock import patch

import pytest

from cam_utils.asterisk import exceptions
from cam_utils.asterisk.ami13 import AMI13

"""Testes relacionados a conexão"""


def test_ami13_initialization():
    ami = AMI13("server", "username", "password")
    assert ami.server == "server"
    assert ami.username == "username"
    assert ami._AMI13__password == "password"
    assert ami.port == 5038
    assert ami.timeout == 5


def test_ami13_initialization_with_custom_parameters():
    ami = AMI13("server", "username", "password", port=5039, timeout=10)
    assert ami.server == "server"
    assert ami.username == "username"
    assert ami._AMI13__password == "password"
    assert ami.port == 5039
    assert ami.timeout == 10


@patch("cam_utils.asterisk.ami13.socket.socket")
def test_ami13_connect(mock_socket):
    ami = AMI13("server", "username", "password")
    ami._AMI13__connect()
    mock_socket.return_value.connect.assert_called_with(("server", 5038))


""" Testes de métodos internos """


def test_ami13_wrong_action():
    ami = AMI13("server", "username", "password")
    with pytest.raises(exceptions.WrongAMIAction):
        ami._AMI13__cmd_parser({"Action": "WrongAction"})


def test_error_response():
    ami = AMI13("server", "username", "password")
    response = ami._AMI13__error_response("Test Error", {"key": "value"})
    assert response == {
        "success": False,
        "message": "Test Error",
        "data": {"key": "value"},
    }


def test_success_response():
    ami = AMI13("server", "username", "password")
    response = ami._AMI13__success_response("Test Success", {"key": "value"})
    assert response == {
        "success": True,
        "message": "Test Success",
        "data": {"key": "value"},
    }


def test_cmd_parser():
    ami = AMI13("server", "username", "password")
    assert (
        ami._AMI13__cmd_parser(
            {"Action": "Login", "Username": "username", "Secret": "password"}
        )
        == b"Action: Login\r\nUsername: username\r\nSecret: password\r\n\r\n"
    )


def test_parse_error():
    raw_error = """
    Response: Error
    Message: Error message
    """
    response_error = {
        "AMIStatus": "Error",
        "Message": "Error message",
    }
    ami = AMI13("server", "username", "password")
    assert ami._AMI13__parse_error(raw_error) == response_error


def test_build_sip_peers():
    data = """
        Event: PeerEntry
        Channeltype: SIP
        ObjectName: 100
        ChanObjectType: peer
        IPaddress: 10.255.255.1
        IPport: 5060
        Dynamic: no
        AutoForcerport: no
        Forcerport: yes
        AutoComedia: no
        Comedia: yes
        VideoSupport: yes
        TextSupport: no
        ACL: yes
        Status: OK (1 ms)
        RealtimeDevice: no
        Description: 
        Accountcode: 

        Event: PeerlistComplete
        EventList: Complete
        ListItems: 50
        """
    result = {
        "100": {
            "Channeltype": "SIP",
            "ObjectName": "100",
            "ChanObjectType": "peer",
            "IPaddress": "10.255.255.1",
            "IPport": "5060",
            "Dynamic": "no",
            "AutoForcerport": "no",
            "Forcerport": "yes",
            "AutoComedia": "no",
            "Comedia": "yes",
            "VideoSupport": "yes",
            "TextSupport": "no",
            "ACL": "yes",
            "Status": "OK (1 ms)",
            "RealtimeDevice": "no",
            "Description": "",
            "Accountcode": "",
        }
    }
    ami = AMI13("server", "username", "password")
    assert ami._AMI13__build_sip_peers(data) == result


def test_parse_sip_peer():
    data = """
Response: Success
Channeltype: SIP
ObjectName: 100
ChanObjectType: peer
SecretExist: Y
RemoteSecretExist: N
MD5SecretExist: N
Context: from-internal
Language: pt-br
ToneZone: <Not set>
AMAflags: Unknown
CID-CallingPres: Presentation Allowed, Not Screened
Callgroup: 1
Pickupgroup: 1
Named Callgroup: 1
Named Pickupgroup: 1
MOHSuggest: 
VoiceMailbox: 100@device
TransferMode: open
LastMsgsSent: 0
Maxforwards: 0
Call-limit: 2147483647
Busy-level: 0
MaxCallBR: 384 kbps
Dynamic: Y
Callerid: "User Name" <100>
RegExpire: 127 seconds
SIP-AuthInsecure: no
SIP-Forcerport: Y
SIP-Comedia: Y
ACL: Y
SIP-CanReinvite: N
SIP-DirectMedia: N
SIP-PromiscRedir: N
SIP-UserPhone: N
SIP-VideoSupport: Y
SIP-TextSupport: N
SIP-T.38Support: Y
SIP-T.38EC: Redundancy
SIP-T.38MaxDtgrm: 400
SIP-Sess-Timers: Accept
SIP-Sess-Refresh: uas
SIP-Sess-Expires: 1800
SIP-Sess-Min: 90
SIP-RTP-Engine: asterisk
SIP-Encryption: N
SIP-RTCP-Mux: N
SIP-DTMFmode: rfc2833
ToHost: 
Address-IP: 10.255.255.1
Address-Port: 5080
Default-addr-IP: (null)
Default-addr-port: 0
Default-Username: 100
Codecs: (ulaw|alaw|opus|h264|h263p|h263)
Status: OK (1 ms)
SIP-Useragent: IPS-300 GPN V4.6.0.0 12027 
Reg-Contact: sip:100@10.255.255.1:5080;transport=udp
QualifyFreq: 60000 ms
Parkinglot: 
SIP-Use-Reason-Header: N
Description: 


    """
    result = {
        "AMIStatus": "Success",
        "Channeltype": "SIP",
        "ObjectName": "100",
        "ChanObjectType": "peer",
        "SecretExist": "Y",
        "RemoteSecretExist": "N",
        "MD5SecretExist": "N",
        "Context": "from-internal",
        "Language": "pt-br",
        "ToneZone": "<Not set>",
        "AMAflags": "Unknown",
        "CID-CallingPres": "Presentation Allowed, Not Screened",
        "Callgroup": "1",
        "Pickupgroup": "1",
        "Named Callgroup": "1",
        "Named Pickupgroup": "1",
        "MOHSuggest": "",
        "VoiceMailbox": "100@device",
        "TransferMode": "open",
        "LastMsgsSent": "0",
        "Maxforwards": "0",
        "Call-limit": "2147483647",
        "Busy-level": "0",
        "MaxCallBR": "384 kbps",
        "Dynamic": "Y",
        "Callerid": '"User Name" <100>',
        "RegExpire": "127 seconds",
        "SIP-AuthInsecure": "no",
        "SIP-Forcerport": "Y",
        "SIP-Comedia": "Y",
        "ACL": "Y",
        "SIP-CanReinvite": "N",
        "SIP-DirectMedia": "N",
        "SIP-PromiscRedir": "N",
        "SIP-UserPhone": "N",
        "SIP-VideoSupport": "Y",
        "SIP-TextSupport": "N",
        "SIP-T.38Support": "Y",
        "SIP-T.38EC": "Redundancy",
        "SIP-T.38MaxDtgrm": "400",
        "SIP-Sess-Timers": "Accept",
        "SIP-Sess-Refresh": "uas",
        "SIP-Sess-Expires": "1800",
        "SIP-Sess-Min": "90",
        "SIP-RTP-Engine": "asterisk",
        "SIP-Encryption": "N",
        "SIP-RTCP-Mux": "N",
        "SIP-DTMFmode": "rfc2833",
        "ToHost": "",
        "Address-IP": "10.255.255.1",
        "Address-Port": "5080",
        "Default-addr-IP": "(null)",
        "Default-addr-port": "0",
        "Default-Username": "100",
        "Codecs": "(ulaw|alaw|opus|h264|h263p|h263)",
        "Status": "OK (1 ms)",
        "SIP-Useragent": "IPS-300 GPN V4.6.0.0 12027",
        "Reg-Contact": "sip:100@10.255.255.1:5080;transport=udp",
        "QualifyFreq": "60000 ms",
        "Parkinglot": "",
        "SIP-Use-Reason-Header": "N",
        "Description": "",
    }
    ami = AMI13("server", "username", "password")
    assert ami._AMI13__parse_sip_peer(data) == result
