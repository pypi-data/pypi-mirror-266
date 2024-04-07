#!/usr/bin/env python3

import os
import json
import uuid
import requests
import shelve
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from client import BaseClient
from .helpers import pick


class Endpoint:

    def __init__(self, parent: "BaseClient") -> None:
        self.parent = parent


class AuthEndpoint(Endpoint):

    token_path = '/tmp/.feishu_token'

    def save_token_to_file(self):
        with shelve.open(self.token_path) as db:
            db['token'] = self.refresh_access_token()
            return True
    
    def fetch_token_from_file(self):
        with shelve.open(self.token_path) as db:
            token = db.get('token')
            return token

    def get_tenant_access_token(self):
        '''
        _summary_

        Returns:
            _type_: _description_
        '''
        if os.environ.get('TENANT_ACCESS_TOKEN'):
            return os.environ.get('TENANT_ACCESS_TOKEN')
        else:
            print('未找到token， 开始刷新')
            resp = self.refresh_access_token()
            if resp.tenant_access_token:
                os.environ['TENANT_ACCESS_TOKEN'] = resp.tenant_access_token
                return os.environ.get('TENANT_ACCESS_TOKEN')

    def refresh_access_token(self):
        payload = dict(
            app_id=self.parent.app_id,
            app_secret=self.parent.app_secret
        )

        token = requests.request(method='POST', 
                                    url=self.parent.options.base_url+'/auth/v3/tenant_access_token/internal', 
                                    json=payload, timeout=5).json()['tenant_access_token']
        
        os.environ['TENANT_ACCESS_TOKEN'] = token
        return token

class MessageEndpoint(Endpoint):

    def send_text(self,
                  text: str,
                  receive_id: str):
        

        format_message_content = json.dumps({ "text": text }, ensure_ascii=False)

        payload = {
                "content": format_message_content,
                "msg_type": "text",
                "receive_id": receive_id,
                "uuid": str(uuid.uuid4())
        }
        receive_id_type = self.parent.extensions.parse_receive_id_type(receive_id=receive_id)

        return self.parent.request(path=f'/im/v1/messages?receive_id_type={receive_id_type}', 
                                   method='POST',
                                   body=payload)
    
    def send_post(self,
                  receive_id: str=None,
                  message_id: str=None,
                  title: str=None,
                  content: list=None):
        '''
        发送富文本消息

        Args:
            reveive_id (str): 必选参数, 接收消息的 id, 可以是 chat_id, 也可以是 openid, 代码会自动判断
            message_id (str): 如果设置此参数, 表示会在原消息上回复消息
            title: (str): 消息的标题
            content: (list): 消息的内容, 示例格式如下
                content = [
                    [
                        {"tag": "text", "text": "VPN: XXX:8443"}
                    ]
                ]

        Returns:
            response (dict): 返回发送消息后的响应, 是一个大的 json, 还在考虑是否拆分一下
        '''
        
        message_content = {
            "zh_cn": {
                "title": title,
                "content": content
                }
            }

        format_message_content = json.dumps(message_content, ensure_ascii=False)
        
        if receive_id:
            receive_id_type = self.parent.extensions.parse_receive_id_type(receive_id=receive_id)
            api = f'/im/v1/messages?receive_id_type={receive_id_type}'
            payload = {
                "content": format_message_content,
                "msg_type": "post",
                "receive_id": receive_id,
                "uuid": str(uuid.uuid4())
            }
            
        elif message_id:
            api = f'/im/v1/messages/{message_id}/reply'
            payload = {
                "content": format_message_content,
                "msg_type": "post",
                "uuid": str(uuid.uuid4())
            }

        return self.parent.request(path=f'/im/v1/messages?receive_id_type={receive_id_type}', 
                                method='POST',
                                body=payload)

    def send_card(self, template_id: str, template_variable: dict=None, receive_id: str=None):
        '''
        目前主要使用的发送卡片消息的函数, 从名字可以看出, 这是第2代的发送消息卡片函数

        Args:
            template_id (str): 消息卡片的 id, 可以在飞书的消息卡片搭建工具中获得该 id
            template_variable (dict): 消息卡片中的变量
            receive_id: (str): 接收消息的 id, 可以填写 open_id、chat_id, 函数会自动检测

        Returns:
            response (dict): 返回发送消息后的响应, 是一个大的 json, 还在考虑是否拆分一下
        '''
        receive_id_type = self.parent.extensions.parse_receive_id_type(receive_id=receive_id)
        content = {
            "type":"template",
            "data":{
                "template_id": template_id,
                "template_variable": template_variable
            }
        }

        content = json.dumps(content, ensure_ascii=False)
        
        payload = {
           	"content": content,
            "msg_type": "interactive",
            "receive_id": receive_id
        }

        return self.parent.request(path=f'/im/v1/messages?receive_id_type={receive_id_type}', 
                                   method='POST',
                                   body=payload)

    def send_file(self, file_name, file_path, receive_id):
        receive_id_type = self.parent.extensions.parse_receive_id_type(receive_id=receive_id)
        content = {
            "file_key": self.parent.extensions.upload_file(file_name=file_name, file_path=file_path)
        }
        content = json.dumps(content, ensure_ascii=False)
        payload = {
            "content": content,
            "msg_type": "file",
            "receive_id": receive_id
        }

        return self.parent.request(path=f'/im/v1/messages?receive_id_type={receive_id_type}', 
                            method='POST',
                            body=payload)

class BitableEndpoint(Endpoint):
    def list_records(self, app_token, table_id):
        return self.parent.request(path=f'/bitable/v1/apps/{app_token}/tables/{table_id}/records',
                                   method='GET')
    
    def add_record(self, app_token, table_id ,fields):
        payload = {
            "fields": fields
        }
        return self.parent.request(path=f'/bitable/v1/apps/{app_token}/tables/{table_id}/records',
                                   method='POST',
                                   body=payload)

    def query_record(self, app_token, table_id, view_id, payload):

        return self.parent.request(path=f'/bitable/v1/apps/{app_token}/tables/{table_id}/records/search',
                                   method='POST',
                                   body=payload)



class ExtensionsEndpoint(Endpoint):
    def parse_receive_id_type(self, receive_id):
        if receive_id.startswith('ou'):
            receive_id_type = 'open_id'
        elif receive_id.startswith('oc'):
            receive_id_type = 'chat_id'
        else:
            raise 'No such named receive_id'

        return receive_id_type

    def upload_file(self, file_name, file_path):

        files = {
            'file_type': ('', 'stream'),
            'file_name': ('', file_name),
            'file': open(file_path, 'rb')
        }

        return self.parent.request(path=f'/im/v1/files',
                                   method='POST',
                                   files=files).data['file_key']

