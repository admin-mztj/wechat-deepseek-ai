import requests

API_URL = "https://api.deepseek.com/v1/chat/completions"
TIMEOUT = 2.0
MAX_TOKENS = 150

FALLBACK_REPLY = "抱歉，AI 还没准备好，请再发一次试试～"


def chat(user_message, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
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
