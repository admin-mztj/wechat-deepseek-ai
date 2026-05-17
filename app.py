import os
import sys

from flask import Flask, request, Response
from dotenv import load_dotenv

from wechat import verify_signature, parse_message, build_text_reply
from deepseek import chat as deepseek_chat

load_dotenv()

WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

app = Flask(__name__)


def xml_response(xml_str):
    return Response(xml_str, content_type="application/xml; charset=utf-8")


@app.route("/wechat", methods=["GET"])
def wechat_verify():
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    echostr = request.args.get("echostr", "")

    print(f"[VERIFY] sig={signature[:10]}... ts={timestamp}", file=sys.stderr)

    if verify_signature(WECHAT_TOKEN, signature, timestamp, nonce):
        return echostr
    return "signature check failed", 403


@app.route("/wechat", methods=["POST"])
def wechat_message():
    xml_data = request.data
    print(f"[MSG] body={xml_data.decode('utf-8', errors='replace')[:300]}", file=sys.stderr)

    from_user = ""
    to_user = ""

    try:
        msg = parse_message(xml_data)
        from_user = msg["from_user"]
        to_user = msg["to_user"]
        print(f"[MSG] type={msg['type']} from={from_user[:20]}", file=sys.stderr)

        if msg["type"] == "text":
            print(f"[MSG] calling DeepSeek...", file=sys.stderr)
            ai_reply = deepseek_chat(msg["content"], DEEPSEEK_API_KEY)
            print(f"[MSG] AI reply len={len(ai_reply)}", file=sys.stderr)
            return xml_response(build_text_reply(from_user, to_user, ai_reply))

        elif msg["type"] == "event":
            event = msg.get("event", "")
            print(f"[MSG] event={event}", file=sys.stderr)
            if event == "subscribe":
                reply = "欢迎关注！我是 AI 助手 🤖\n\n直接发消息就可以和我聊天。\n\n现在就开始吧～"
                return xml_response(build_text_reply(from_user, to_user, reply))
            elif event == "CLICK":
                reply = deepseek_chat(msg.get("event_key", ""), DEEPSEEK_API_KEY)
                return xml_response(build_text_reply(from_user, to_user, reply))

        return xml_response(build_text_reply(from_user, to_user, "暂不支持此消息类型"))

    except Exception as e:
        import traceback
        err = traceback.format_exc()
        print(f"[MSG] ERROR: {err}", file=sys.stderr)
        return xml_response(build_text_reply(from_user, to_user, f"系统错误：{str(e)[:80]}"))


@app.route("/debug", methods=["GET", "POST"])
def debug_info():
    return {
        "method": request.method,
        "content_type": request.content_type,
        "body": request.data.decode("utf-8", errors="replace")[:500],
        "args": dict(request.args),
        "headers": dict(request.headers),
    }


@app.route("/test", methods=["GET"])
def test_api():
    msg = request.args.get("msg", "你好")
    try:
        reply = deepseek_chat(msg, DEEPSEEK_API_KEY)
        return f"DeepSeek OK: {reply}"
    except Exception as e:
        return f"DeepSeek FAIL: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
