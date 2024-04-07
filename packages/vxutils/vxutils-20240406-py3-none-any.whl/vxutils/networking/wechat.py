"""wechat 通知接口"""

import time
import logging
from typing import List, Dict, Optional, Union, Collection, Any
import json
import httpx
from concurrent.futures import Future
from vxutils.decorators import async_task

__all__ = ["vxWeChatBot", "vxWeChatClient"]


class vxWeChatClient:
    """微信消息发送类"""

    def __init__(
        self, corpid: str, secret: str, agentid: str, timeout: int = 5
    ) -> None:
        """
        微信客户端
        """
        self._corpid = corpid
        self._secret = secret
        self._agentid = agentid
        self._timeout = timeout
        self._access_token = ""
        self._expire_time = time.time() - 1

    @property
    def token(self) -> str:
        """
        获取access_token

        请求方式： GET（HTTPS）
        请求地址： https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=ID&corpsecret=SECRET

        返回结果:
        {
            "errcode": 0,
            "errmsg": "ok",
            "access_token": "accesstoken000001",
            "expires_in": 7200
        }
        """
        if (not self._access_token) or self._expire_time < time.time():
            resp = httpx.get(
                f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self._corpid}&corpsecret={self._secret}",
                timeout=self._timeout,
            )
            resp.raise_for_status()
            ret_mesg = json.loads(resp.text)
            if ret_mesg.get("errcode") != 0:
                logging.warning("获取access_token失败. %s", ret_mesg)
                raise ConnectionError(f"获取access_token失败. {ret_mesg}")

            self._access_token: str = ret_mesg.get("access_token")
            self._expire_time = time.time() + ret_mesg.get("expires_in", 0) - 10
            logging.info(
                "更新access_token: %s， 过期时间: %s",
                self._access_token,
                self._expire_time,
            )

        return self._access_token

    def send_message(
        self,
        markdown_content: Dict[str, str],
        users: Optional[List[str]] = None,
        parties: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        发送企业微信markdown消息

        请求方式：POST（HTTPS）
        请求地址： https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=ACCESS_TOKEN

        body:为消息内容
        {
            "touser" : users or "@all",
            "toparty" : "PartyID1|PartyID2",
            "totag" : "TagID1 | TagID2",
            "msgtype": "markdown",
            "agentid" : 1,
            "markdown": {
                    "content": "您的会议室已经预定，稍后会同步到`邮箱`
                        >**事项详情**
                        >事　项：<font color=\"info\">开会</font>
                        >组织者：@miglioguan
                        >参与者：@miglioguan、@kunliu、@jamdeezhou、@kanexiong、@kisonwang
                        >
                        >会议室：<font color=\"info\">广州TIT 1楼 301</font>
                        >日　期：<font color=\"warning\">2018年5月18日</font>
                        >时　间：<font color=\"comment\">上午9:00-11:00</font>
                        >
                        >请准时参加会议。
                        >
                        >如需修改会议信息，请点击：[修改会议信息](https://work.weixin.qq.com)"
            },
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        """
        post_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.token}"
        msg = {
            "touser": "|".join(users) if users else "@all",
            "toparty": "|".join(parties) if parties else "",
            "totag": "|".join(tags) if tags else "",
            "msgtype": "markdown",
            "agentid": self._agentid,
            "markdown": {"content": markdown_content},
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800,
        }
        resp = httpx.post(post_url, json=msg, timeout=self._timeout)
        resp.raise_for_status()
        ret_msg = json.loads(resp.text)
        if ret_msg.get("errcode") != 0:
            logging.error("发送消息失败. %s", ret_msg)
            raise ConnectionError(f"发送消息失败. {ret_msg}")

        return str(ret_msg.get("msgid", ""))


class vxWeChatBot:
    """微信群聊天机器人"""

    def __init__(self, url: str) -> None:
        self._url = url

    @async_task(3)
    def send_message(self, message: Dict[str, Collection[str]]) -> bool:
        """发送消息"""

        headers = {"Content-Type": "application/json"}
        resp = httpx.post(
            self._url,
            json=message,
            headers=headers,
            timeout=5,
        )
        resp.raise_for_status()
        ret_message = json.loads(resp.text)
        if ret_message["errcode"] != 0:
            raise ValueError(ret_message)
        logging.debug("发送消息成功. %s", ret_message)

        return True

    def send_text(
        self,
        content: Union[str, Dict[str, str]],
        mentioned_list: Optional[List[str]] = None,
        mentioned_mobile_list: Optional[List[str]] = None,
    ) -> Any:
        """发送文本消息"""
        if mentioned_list is None:
            mentioned_list = []

        if mentioned_mobile_list is None:
            mentioned_mobile_list = []

        msgs = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": mentioned_list,
                "mentioned_mobile_list": mentioned_mobile_list,
            },
        }
        return self.send_message(msgs)

    def send_markdown(self, content: str) -> Any:
        """发送markdown消息"""
        msgs = {
            "msgtype": "markdown",
            "markdown": {"content": content, "mentioned_list": ["@all"]},
        }
        return self.send_message(msgs)

    def send_news(self, *articles: Collection[str]) -> Any:
        """发送图文消息"""
        msgs = {
            "msgtype": "news",
            "news": {"articles": articles},
        }
        return self.send_message(msgs)

    def send_notice(self, **content: Dict[str, Collection[str]]) -> Any:
        """发送模板消息"""
        msgs = {
            "msgtype": "template_card",
            "template_card": {
                "card_type": "text_notice",
                "source": {
                    "icon_url": "",
                    "desc": "",
                    "desc_color": 0,
                },
                "main_title": {"title": "empty", "desc": ""},
                "emphasis_content": {"title": "", "desc": ""},
                "quote_area": {
                    "type": 1,
                    "url": "http://example.com",
                    "title": "",
                    "quote_text": "",
                },
                "sub_title_text": "",
                "horizontal_content_list": [
                    {
                        "keyname": "empty",
                        "value": "",
                    }
                ],
                "jump_list": [],
                "card_action": {
                    "type": 1,
                    "url": "http://example.com",
                    "appid": "",
                    "pagepath": "",
                },
            },
        }
        msgs["template_card"].update(content)
        return self.send_message(msgs)


if __name__ == "__main__":
    wechat = vxWeChatBot(
        "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=7bdc2000-348c-4c7b-8ec3-08d0d177f0bc"
    )
    # a = wechat.send_text("hello world111111")
    # print("send....")
    # print(a)
    # time.sleep(1)
    for i in range(30):
        wechat.send_text(f"hello world{i}")
    print("send....")
