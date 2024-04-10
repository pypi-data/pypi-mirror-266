import base64
import hashlib
import hmac
import json
import time

from .base import BaseNotification
import requests


class DingtalkNotification(BaseNotification):
    """
    钉钉 Webhook 机器人。
    文档地址: https://open.dingtalk.com/document/orgapp/robot-message-types-and-data-format#title-z74-8to-i7e
    """

    def __init__(self, webhook_url: str, secret: str):
        """
        初始化 webhook 消息发送器, 暂时只使用签名方式
        :param webhook_url: webhook 的 url 地址
        :param secret: 使用签名方式，签名密钥
        """
        self._url = webhook_url
        self._secret = secret
        self._secret_enc = secret.encode('utf8')
        self._header = {
            "Content-Type": "application/json"
        }

    def _secret_params(self) -> dict:
        """
        获取签名参数
        :return: 签名参数字典
        """
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f'{timestamp}\n{self._secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(self._secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code)
        # sign = urllib.parse.quote_plus(tmp)
        return {
            "timestamp": timestamp,
            "sign": sign
        }

    def _send(self, data: dict):
        """
        发送消息
        :param data: 要发送的消息的字典，必须满足 api 给定的格式
        """
        resp = requests.post(self._url, params=self._secret_params(), data=json.dumps(data), headers=self._header)
        print(resp.text)

    def send_text(self, txt: str):
        """
        发送文本消息
        :param txt: 文本消息的内容
        """
        self._send({
            "text": {
                "content": txt
            },
            "msgtype": "text"
        })

    def send_markdown(self, markdown: str, title: str):
        """
        发送 markdown 类型的消息
        :param title: 消息标题：消息列表看到的新消息暂时的内容
        :param markdown: markdown 格式的数据内容
        """
        self._send({
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": markdown
            },
        })
