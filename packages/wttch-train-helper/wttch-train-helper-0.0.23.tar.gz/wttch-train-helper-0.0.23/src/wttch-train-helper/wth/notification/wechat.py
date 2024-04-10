import json

import requests

from .base import BaseNotification


class WechatNotification(BaseNotification):
    """
    企业微信 webhook 消息发送器.
    API 地址: https://developer.work.weixin.qq.com/document/path/91770
    """

    def __init__(self, webhook_url):
        """
        初始化器
        :param webhook_url: 机器人的 webhook 地址
        """
        self._url = webhook_url
        self._header = {
            "Content-Type": "application/json"
        }

    def send_text(self, txt: str):
        """
        发送文本消息
        :param txt: 文本消息内容
        """
        self._send({
            "msgtype": "text",
            "text": {
                "content": txt
            }
        })

    def send_markdown(self, markdown: str):
        """
        发送 markdown 格式的数据消息
        :param markdown: 消息内容
        """
        self._send({
            "msgtype": "markdown",
            "markdown": {
                "content": markdown
            }
        })

    def _send(self, data: dict):
        """
        发送消息
        :param data: 企业微信的数据 body
        """
        resp = requests.post(self._url, data=json.dumps(data), headers=self._header)
        print(resp.text)
