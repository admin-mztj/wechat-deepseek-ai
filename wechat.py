import hashlib
import time
import xml.etree.ElementTree as ET


def verify_signature(token, signature, timestamp, nonce):
    tmp_list = sorted([token, timestamp, nonce])
    tmp_str = "".join(tmp_list)
    return hashlib.sha1(tmp_str.encode()).hexdigest() == signature


def parse_message(xml_data):
    root = ET.fromstring(xml_data)

    msg = {
        "type": root.find("MsgType").text,
        "from_user": root.find("FromUserName").text,
        "to_user": root.find("ToUserName").text,
    }

    if msg["type"] == "text":
        msg["content"] = root.find("Content").text
    elif msg["type"] == "event":
        msg["event"] = root.find("Event").text
        event_key_el = root.find("EventKey")
        msg["event_key"] = event_key_el.text if event_key_el is not None else ""

    return msg


def build_text_reply(to_user, from_user, content):
    return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""
