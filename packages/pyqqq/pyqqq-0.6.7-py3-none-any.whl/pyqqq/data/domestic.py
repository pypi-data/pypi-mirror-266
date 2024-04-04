from pyqqq import get_api_key
from pyqqq.utils.retry import retry
import datetime as dtm
import pandas as pd
import pyqqq.config as c
import requests


def get_alert_stocks(alert_type: str, date: dtm.date = None) -> pd.DataFrame | None:
    """
    시장 경보 종목을 조회합니다.

    Args:
        alert_type (str): 경보종류. caution:투자주의종목 warning:투자경고종목 risk:투자위험종목
        date (dtm.date, optional): 조회할 날짜. 기본값은 None (가장 최근 데이터)

    Returns:
        pd.DataFrame|None: 경보 종목 리스트. 해당일에 저장된 데이터가 없으면 None, 저장되었지만 지정 종목이 없으면 빈 DataFrame이 반환됩니다.

        - code (str, index): 종목코드
        - name (str): 종목명
        - current_price (int): 현재가
        - change (int): 전일대비가격
        - change_rate (float): 전일대비등락율
        - volume (int): 거래량
        - bid_price (int): 매수호가
        - ask_price (int): 매도호가
        - per (float): PER

    Examples:
        >>> df = get_alert_stocks('caution')
        >>> print(df.head())
                    name  current_price  change  change_rate   volume  bid_price  ask_price    per
        code
        402340   SK스퀘어          77600    2400        -3.00   303590      77000      76900  -8.49
        053950    경남제약           1570       1         0.06  4857452       1569       1568  -4.91
        012320  경동인베스트         113100   11800        11.65   994188     118800     118700  22.05
        002720    국제약품           6820     310        -4.35  5559738       6900       6890 -17.14
        219420  링크제니시스           9100     160         1.79  1720993       9120       9100  83.49
    """
    url = f"{c.PYQQQ_API_URL}/domestic-stock/alert-stocks/{alert_type}"
    params = {}
    if date:
        params["date"] = date

    r = _send_request("GET", url, params=params)
    if r.status_code == 404:
        return None
    else:
        _raise_for_status(r)

        df = pd.DataFrame(r.json())
        if not df.empty:
            df.set_index("code", inplace=True)
        return df


def get_management_stocks(date: dtm.date = None) -> pd.DataFrame | None:
    """
    관리종목을 조회합니다.

    Args:
        date (dtm.date, optional): 조회할 날짜(지정일이 아닌 데이터 수집일). 기본값은 None (가장 최근 데이터)

    Returns:
        pd.DataFrame|None: 관리종목 리스트. 해당일에 저장된 데이터가 없으면 None, 저장되었지만 지정 종목이 없으면 빈 DataFrame이 반환됩니다.

        - code (str, index): 종목코드
        - name (str): 종목명
        - current_price (int): 현재가
        - change (int): 전일대비가격
        - change_rate (float): 전일대비등락율
        - volume (int): 거래량
        - designation_date (str): 지정일
        - designation_reason (str): 지정사유

    Examples:
        >>> df = get_management_stocks()
        >>> print(df.head())
                   name  current_price  change  change_rate  volume designation_date designation_reason
        code
        001140       국보           2110       0         0.00       0       2024.03.22          감사의견 의견거절
        006380      카프로            732       0         0.00       0       2024.03.22          감사의견 의견거절
        093230     이아이디           1392       0         0.00       0       2024.03.22          감사의견 의견거절
        363280   티와이홀딩스           3205     150        -4.47  393547       2024.03.22  감사범위제한으로인한 감사의견한정
        36328K  티와이홀딩스우           4940     560       -10.18   26011       2024.03.22  감사범위제한으로인한 감사의견한정
    """
    url = f"{c.PYQQQ_API_URL}/domestic-stock/management-stocks"
    params = {}
    if date:
        params["date"] = date

    r = _send_request("GET", url, params=params)
    if r.status_code == 404:
        return None
    else:
        _raise_for_status(r)

        df = pd.DataFrame(r.json())
        if not df.empty:
            df.set_index("code", inplace=True)
        return df


@retry(requests.HTTPError)
def _send_request(method: str, url: str, **kwargs):
    api_key = get_api_key()
    if not api_key:
        raise ValueError("API key is not set")

    return requests.request(
        method=method,
        url=url,
        headers={"Authorization": f"Bearer {api_key}"},
        **kwargs,
    )


def _raise_for_status(r: requests.Response):
    if r.status_code != 200:
        print(r.text)

    r.raise_for_status()
