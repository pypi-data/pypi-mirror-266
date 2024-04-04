# -*- coding: utf-8 -*-

import copy
import random
from ..log import logger
import sys

PY2 = sys.version_info[0] == 2
if PY2:
    from slackclient import SlackClient as SendClient
else:
    from slack_sdk import WebClient as SendClient


class SlackFlyLogBackend(object):
    """
    发送tele
    """

    def __init__(self, sender_list):
        """
        初始化
        sender_list可以保证只要发送失败就尝试下一个
        """
        self.sender_list = sender_list

    def emit(self, title, content, receiver_list):
        """
        发送
        """

        sender_list = copy.deepcopy(self.sender_list)
        logger.error("sender_list %s", sender_list)

        while sender_list:
            random.shuffle(sender_list)

            # 取出最后一个
            params = sender_list.pop()

            try:
                logger.error("params %s", params)
                channel_id = params['channel_id']
                slack_token = params['slack_token']
                self._send_msg_to_slack(channel_id, slack_token, content, title)
                return True
            except:
                logger.error('exc occur. params: %s', params, exc_info=True)
        else:
            # 就是循环完了，也没发送成功
            return False

    def _send_msg_to_slack(self, channel_id, slack_token, send_msg, title):
        """
        :param channel_id: 接收渠道ID
        :param slack_token: slack_token
        :param send_msg: 发送内容
        :return:
        """


        if not send_msg and not title:
            return False

        msg = '\n\n'.join([title, send_msg])
        if '%0a' in msg:
            msg = msg.replace('%0a', '\n')

        # 增加@功能
        msg = '{msg}\n<!channel>'.format(msg=msg)


        if PY2:
            sc = SendClient(slack_token)
            # 发送消息
            sc.api_call(
                "chat.postMessage",
                channel=channel_id,
                text=msg
            )

        else:
            # Python3 发送
            sc = SendClient(token=slack_token)

            sc.chat_postMessage(channel=channel_id, text=msg)

        return True
