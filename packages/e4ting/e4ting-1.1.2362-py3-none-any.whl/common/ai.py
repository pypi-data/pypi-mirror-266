
# import openai
# openai.api_key = "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"
# prompt = "Once upon a time"
# model = "text-davinci-002"
# response = openai.Completion.create(
#     engine=model,
#     prompt=prompt,
#     max_tokens=100,
#     n=1,
#     stop=None,
#     temperature=0.5,
# )
# text = response.choices[0].text
# print(text)

import socks
import socket
import openai
import os

socks.set_default_proxy(socks.SOCKS5, "172.31.50.25", 1080)
socket.socket = socks.socksocket

# 设置 OpenAI API 密钥
openai.api_key = "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" # os.environ["OPENAI_API_KEY"]

# GPT4 密钥
# openai.api_key = "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"

# 设置 HTTP 代理
proxies = {'http': 'http://172.31.50.25:808'}

# 连接到 OpenAI API
openai.api_base = "https://api.openai.com/v1"
# openai.api_base_kwargs = {'proxies': proxies}
response = openai.Completion.create(
    engine="text-davinci-003",
    prompt="如何评价Python",
    max_tokens=4000,
)

# 输出响应
print(response.choices[0].text)