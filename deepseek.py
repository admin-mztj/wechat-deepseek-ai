import requests

API_URL = "https://api.deepseek.com/v1/chat/completions"
TIMEOUT = 4.5
MAX_TOKENS = 500

SYSTEM_PROMPT = """你是微信公众号 AI 助手，请遵循以下规则：
- 回复简洁，控制在 200 字以内
- 用中文回复
- 友好、有帮助
- 遇到不懂的问题诚实说明"""

FALLBACK_REPLY = "抱歉，AI 响应超时了，请再发一次消息试试～\n\n💡 小提示：问题越具体，回复越快哦"


def chat(user_message, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.Timeout:
        return FALLBACK_REPLY
    except requests.RequestException as e:
        return f"抱歉，服务暂时不可用，请稍后再试。\n错误信息：{str(e)[:50]}"
