# -*- coding: utf-8 -*-

import os
import requests

# 定义消息标记常量
message_mark_0: str = 'Message'
message_mark_A: str = '[脑暴]'
message_mark_B: str = '[赞]'
message_mark_C: str = '[加油]'
message_mark_D: str = '[算账]'

msg_text = '''{
    "msgtype": "text",
    "text": {
        "content": "%s"
    }
}'''


def dingtalk_message(data, webhook=None):
    """
    发送钉钉消息。

    根据给定的数据，通过钉钉机器人的Webhook发送消息。

    参数：
        data: 消息数据。
        webhook: Webhook地址（默认为环境变量'DINGTALK_WEBHOOK'）。

    返回：
        str: 发送结果。

    异常：
        None
    """
    webhook = os.environ.get( 'DINGTALK_WEBHOOK' )  if webhook is None else webhook
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post( webhook, headers=headers, data=data.encode( "UTF-8" ) )
    return response.text


def qywechat_message(data, webhook=None):
    """
    发送企业微信消息。

    根据给定的数据，通过企业微信的机器人的Webhook发送消息。

    参数：
        data: 消息数据。
        webhook: Webhook地址（默认为环境变量'QYWECHAT_WEB

    返回：
        str: 发送结果。

    异常：
        None
    """
    webhook = os.environ.get( 'QYWECHAT_WEBHOOK' ) if webhook is None else webhook
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post( webhook, headers=headers, data=data.encode( "UTF-8" ) )
    return response.text


def qywechat_text_message(text: str, webhook=None):
    """
    发送企业微信文本消息。

    根据给定的文本内容，通过企业微信机器人发送文本消息。

    参数：
        text (str): 文本内容。
        webhook: Webhook地址（默认为环境变量'QYWECHAT_WEBHOOK'）。


    返回：
        None

    异常：
        None
    """
    qywechat_message( msg_text % text, webhook=webhook)


def dingtalk_text_message(text: str, webhook=None):
    """
    发送钉钉文本消息。

    根据给定的文本内容，通过钉钉机器人发送文本消息。

    参数：
        text (str): 文本内容。
        webhook: Webhook地址（默认为环境变量'DINGTALK_WEBHOOK'）。

    返回：
        None

    异常：
        None
    """
    dingtalk_message( msg_text % text, webhook=webhook)
