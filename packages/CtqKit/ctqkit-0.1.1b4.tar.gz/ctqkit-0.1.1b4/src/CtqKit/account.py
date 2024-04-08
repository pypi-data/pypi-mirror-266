import json
import time
from functools import wraps
from typing import Optional

import requests


class Account:
    """
    天衍量子计算云平台账号
    """

    def __init__(
            self,
            login_key: Optional[str] = None,
            machine_name: Optional[str] = None,
            base_url: Optional[str] = 'https://qc.zdxlz.com',
            login_url: Optional[str] = None,
            auto_login: bool = True,
            auto_reconnect: bool = True,
    ):
        """
        account initialization

        Args:
            login_key:
                API Token under personal center on the web.
            machine_name:
                name of quantum computer.
            base_url:
                System API base url.
            login_url:
                System Login API url.

        Raises:
            Exception: throw an exception when login fails
        """
        self.login_key = login_key
        self.machine_name = machine_name
        self.access_token = None
        self.expire_time = None

        self.base_url = base_url
        self.login_url = login_url or f'{self.base_url}/qccp-auth/oauth2/opnId'
        self.auto_reconnect = auto_reconnect
        if auto_login:
            self.log_in()

    def log_in(self):
        """
        login to platform
        :return:
        """
        data = {
            'grant_type': 'openId',
            'client_id': 'EDJvCEU+cqjQCEOW7SPhCg==',
            'OpenId': self.login_key,
            'account_type': 'member'
        }

        res = requests.post(url=self.login_url, data=data)
        status_code = res.status_code
        send_req_time = time.time()
        if status_code != 200:
            raise Exception(f'Login failed, request interface failed, status_code:{status_code}')
        result = res.json()
        if result.get('code', -1) != 200:
            msg = result.get('msg', 'login failed')
            raise Exception(f'Login failed：{msg}')
        try:
            if (data := result.get('data')) and isinstance(data, dict):
                self.access_token = data.get('access_token')
                # self.refresh_token = data.get('refresh_token')
                self.expire_time = data.get('expires_in') + send_req_time
        except Exception:
            raise Exception(f'Login failed')

    @staticmethod
    def reconnect(func):
        """
        before send request，check token expire time
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.access_token:
                raise Exception('Please log in to the platform first')
            if self.auto_reconnect and self.expire_time and self.expire_time > int(time.time()):
                self.log_in()
            return func(self, *args, **kwargs)

        return wrapper
