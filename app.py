import os

from flask import Flask, request
from dotenv import load_dotenv

from wechat import verify_signature, parse_message, build_text_reply
from deepseek import chat as deepseek_chat

load_dotenv()

WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

app = Flask(__name__)


@app.route("/wechat", methods=["GET"])
def wechat_verify():
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    echostr = request.args.get("echostr", "")

    if verify_signature(WECHAT_TOKEN, signature, timestamp, nonce):
        return echostr
    return "signature check failed", 403


@app.route("/wechat", methods=["POST"])
def wechat_message():
    try:
        xml_data = request.data
        msg = parse_message(xml_data)

        if msg["type"] == "text":
            ai_reply = deepseek_chat(msg["content"], DEEPSEEK_API_KEY)
            return build_text_reply(msg["from_user"], msg["to_user"], ai_reply)

        elif msg["type"] == "event":
            event = msg.get("event", "")
            if event == "subscribe":
                reply = "欢迎关注！我是 AI 助手 🤖\n\n直接发消息就可以和我聊天，无论是提问、翻译、写作还是闲聊，我都能帮你。\n\n现在就开始吧～"
                return build_text_reply(msg["from_user"], msg["to_user"], reply)
            elif event == "CLICK":
                reply = deepseek_chat(msg.get("event_key", ""), DEEPSEEK_API_KEY)
                return build_text_reply(msg["from_user"], msg["to_user"], reply)

        return "success"

    except Exception as e:
        return f"<xml><ToUserName><![CDATA[]]></ToUserName><FromUserName><![CDATA[]]></FromUserName><CreateTime>0</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[服务异常：{str(e)[:100]}]]></Content></xml>"


@app.route("/test", methods=["GET"])
def test_api():
    msg = request.args.get("msg", "你好，用一句话介绍你自己")
    try:
        reply = deepseek_chat(msg, DEEPSEEK_API_KEY)
        return f"DeepSeek OK: {reply}"
    except Exception as e:
        return f"DeepSeek FAIL: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
