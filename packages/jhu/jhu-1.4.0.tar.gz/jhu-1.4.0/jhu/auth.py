"""
整合钉钉,飞书第三方网页登录
"""

from urllib.parse import quote_plus
from enum import Enum
from requests import post, get


class AuthType(Enum):
    DINGDING = 0
    FEISHU = 1


def dingding_user_info_get(ak: str, sk: str, auth_code: str) -> dict:
    # 获取Access_token
    ACCESS_TOKEN_URL = 'https://api.dingtalk.com/v1.0/oauth2/userAccessToken'
    data = dict(clientId=ak, clientSecret=sk,
                code=auth_code, grantType='authorization_code')
    with post(ACCESS_TOKEN_URL, json=data) as rsp:
        access_token = rsp.json().get('accessToken', '')

    # 获取UserInfo
    USER_INFO_URL = 'https://api.dingtalk.com/v1.0/contact/users/me'
    headers = {'x-acs-dingtalk-access-token': f'{access_token}'}
    with get(USER_INFO_URL, headers=headers) as rsp:
        results = rsp.json()
    return results


def feishu_user_info_get(ak: str, sk: str, auth_code: str) -> dict:
    # 1.获取app_access_token
    app_access_token_data = dict(app_id=ak, app_secret=sk)
    APP_ACCESS_TOKEN_URL = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal'
    with post(APP_ACCESS_TOKEN_URL, json=app_access_token_data) as rsp:
        app_access_token = rsp.json().get('app_access_token', '')

    # 2.获取access_token
    ACCESS_TOKEN_URL = 'https://open.feishu.cn/open-apis/authen/v1/oidc/access_token'
    access_token_headers = dict(Authorization=f'Bearer {app_access_token}')
    access_token_data = dict(
        grant_type='authorization_code', code=auth_code)
    with post(ACCESS_TOKEN_URL, headers=access_token_headers, json=access_token_data) as rsp:
        user_access_token = rsp.json()['data']['access_token']

    # 3.获取用户信息
    USER_INFO_URL = 'https://open.feishu.cn/open-apis/authen/v1/user_info'
    user_access_token_headers = dict(
        Authorization=f'Bearer {user_access_token}')
    with get(USER_INFO_URL, headers=user_access_token_headers) as rsp:
        result = rsp.json()
    return result


class ThridAuth:
    def __init__(self, ak: str, sk: str, auth_type: AuthType) -> None:
        """三方扫码登录初始化

        Args:
            ak:str,应用的appkey
            sk:str,应用的secretkey
            auth_type:AuthType,应用类型,当前支持 钉钉:AuthType.DINGDING,飞书:AuthType.FEISHU
        """
        self.auth_type = auth_type
        self.ak = ak
        self.sk = sk

    def login_url_generate(self, redirect_url: str, state: str = None) -> str:
        """生成三方扫码登录的url地址

        Args:
            redirect_url:str,扫码通过后,回调的地址
            state:str,生成地址用的state

        Return:
            三方扫码登录的url地址:str
        """
        match(self.auth_type):
            case AuthType.DINGDING:
                state = state or 'JHU_DINGDING'
                # 钉钉三方登录网页地址拼接
                prefix_url = 'https://login.dingtalk.com/oauth2/challenge.htm'
                data = dict(
                    redirect_uri=quote_plus(redirect_url),
                    client_id=self.ak,
                    response_type='code', scope='openid', state=state, prompt='consent'
                )
            case AuthType.FEISHU:
                # 飞书三方登录网页地址拼接
                state = state or 'JHU_FEISHU'
                prefix_url = 'https://open.feishu.cn/open-apis/authen/v1/authorize'
                data = dict(
                    redirect_uri=quote_plus(redirect_url),
                    app_id=self.ak,
                    scope='contact:user.phone:readonly',
                    state=state
                )
            case _:
                raise Exception('认证类型类型错误')

        query_params = '&'.join([f'{k}={data[k]}' for k in data])
        url = prefix_url+'?'+query_params
        return url

    def get_user_info(self, auth_code: str) -> dict:
        """获取三方扫码得到的用户信息

        Args:
            auth_code:str,三方登录连接返回的auth_code

        Return:
            用户的json信息:dict
        """
        match(self.auth_type):
            case AuthType.DINGDING:
                result = dingding_user_info_get(self.ak, self.sk, auth_code)
            case AuthType.FEISHU:
                result = feishu_user_info_get(self.ak, self.sk, auth_code)
            case _:
                raise Exception('认证类型类型错误')
        return result


if __name__ == '__main__':
    ding_ak = 'ding_ak'
    ding_sk = 'ding_sk'
    d = ThridAuth(ding_ak, ding_sk, AuthType.DINGDING)
    d.login_url_generate('http://localhost:9000/')
    # 这里的code从redirect_url返回的code中获取
    d.get_user_info('74f4f8d7dcdc3942ac11ef963f8fc76d')

    feishu_ak = 'feishu_ak'
    feishu_sk = 'feishu_sk'
    f = ThridAuth(feishu_ak, feishu_sk, AuthType.FEISHU)
    f.login_url_generate('http://localhost:9000/')
    # 这里的code从redirect_url返回的code中获取
    f.get_user_info('40dta314d73246698df628d448d2c439')
