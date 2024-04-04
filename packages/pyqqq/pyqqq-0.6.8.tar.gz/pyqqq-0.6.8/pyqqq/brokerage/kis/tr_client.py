from pyqqq.brokerage.kis.oauth import KISAuth
from pyqqq.utils.logger import get_logger
from pyqqq.utils.retry import retry
import requests

class KISTRClient:
    logger = get_logger("KISTRClient")

    '''
    한국투자증권 TR 요청을 위한 클라이언트

    Args:
        auth (KISAuth): 인증 정보를 담고 있는 객체
        corp_data (dict): 기업 고객의 경우 추가로 필요한 정보를 담고 있는 객체
    '''
    def __init__(self, auth: KISAuth, corp_data: dict = None):
        self.auth = auth
        self.corp_data = corp_data

    @retry(requests.HTTPError)
    def request(self, path: str, tr_id: str, tr_cont: str = '', params: dict = None, body: dict = None, method: str = 'GET'):
        '''
        TR 요청을 보내고 응답을 받는 메서드

        Args:
            path (str): 요청을 보낼 URL 경로
            tr_id (str): TR ID
            tr_cont (str): TR CONT
            params (dict): URL 쿼리 파라미터
            body (dict): 요청 바디
            method (str): HTTP 메서드

        Returns:
            tuple: 응답 바디와 응답 헤더를 담은 튜플

        Raises:
            requests.HTTPError: 요청이 실패한 경우
        '''
        headers = {
            'content-type': 'application/json; charset=utf-8',
            'authorization': f'Bearer {self.auth.get_token()}',
            'appkey': self.auth.appkey,
            'appsecret': self.auth.appsecret,
            'custtype': 'P' if self.corp_data is None else 'B',
            'tr_id': tr_id,
            'tr_cont': tr_cont,
        }
        if self.corp_data is not None:
            headers.update(self.corp_data)

        url = f"{self.auth.host_url}{path}"

        r = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=body
        )

        if r.status_code != 200:
            try:
                res_body = r.json()
                if "msg_cd" in res_body and res_body["msg_cd"] == "EGW00123":
                    self.auth.get_token(True)

            except Exception as e:
                self.logger.exception(e)
            print(r.text)
            r.raise_for_status()

        response_headers = r.headers
        response_body = r.json()

        return response_body, response_headers
