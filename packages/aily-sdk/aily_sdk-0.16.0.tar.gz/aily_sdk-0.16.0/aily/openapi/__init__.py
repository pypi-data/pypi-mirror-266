import requests
from loguru import logger


class OpenAPIClient:
    def __init__(self, user_access_token=None, app_id=None, app_secret=None):
        self.token = None
        if user_access_token:
            self.token = user_access_token
        if app_id and app_secret:
            self.token = self.get_tenant_access_token(app_id, app_secret)

    def use_user_access_token(self, user_access_token):
        self.token = user_access_token

    def use_tenant_access_token(self, tenant_access_token=None, app_id=None, app_secret=None):
        if tenant_access_token:
            self.token = tenant_access_token

        if app_id and app_secret:
            self.token = self.get_tenant_access_token(app_id, app_secret)

    @staticmethod
    def get_tenant_access_token(app_id, app_secret):
        url = "https://open.larkoffice.com/open-apis/auth/v3/tenant_access_token/internal"

        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }

        data = {
            "app_id": app_id,
            "app_secret": app_secret
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            code = result.get("code")
            if code == 0:
                return result.get("tenant_access_token")
            else:
                logger.info(f"获取 tenant_access_token 失败,错误码: {code}, 错误信息: {result.get('msg')}")
        else:
            logger.info(f"请求失败,状态码: {response.status_code}, 错误信息: {response.text}")

        return None

    def get(self, url, headers=None, data=None, query=None):
        _headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        if headers:
            _headers.update(headers)
        resp = requests.get(url, headers=_headers, json=data, params=query)

        logger.info(f'logid= {resp.headers["X-Tt-Logid"]} content= {resp.content}')
        return resp.json()

    def post(self, url, headers=None, data=None, query=None):
        _headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        if headers:
            _headers.update(headers)
        resp = requests.post(url, headers=_headers, json=data, params=query)
        logger.info(f'logid= {resp.headers["X-Tt-Logid"]} content= {resp.content}')
        return resp.json()
