from pyqqq.utils.logger import get_logger
import datetime as dtm
import pandas as pd
import pyqqq
import pyqqq.config as c
import pytz
import requests

logger = get_logger("realtime")


def get_all_last_trades():
    """
    모든 종목의 최근 체결 정보를 반환합니다.

    Returns:
        list:
        - dict:
            - chetime (str): 체결시간
            - sign (str): 전일대비구분
            - change (int): 전일대비가격
            - drate (float): 전일대비등락율
            - price (int): 체결가
            - opentime (str): 시가시간
            - open (int): 시가
            - hightime (str): 고가시간
            - high (int): 고가
            - lowtime (str): 저가시간
            - low (int): 저가
            - cgubun (str): 체결구분
            - cvolume (int): 체결량
            - value (int): 누적거래대금
            - mdvolume (int): 매도체결수량
            - mdchecnt (int): 매도체결건수
            - msvolume (int): 매수체결수량
            - mschecnt (int): 매수체결건수
            - cpower (float): 체결강도
            - offerho (int): 매도호가
            - bidho (int): 매수호가
            - status (str): 장정보
            - jnilvolume (int): 전일거래량
            - shcode (str): 종목코드

    """

    r = requests.get(f"{c.PYQQQ_API_URL}/domestic-stock/trades")
    r.raise_for_status()

    data = r.json()
    result = [data[k] for k in data.keys()]

    return result


def get_all_minute_data(
    time: dtm.datetime, include_empty: bool = False
) -> pd.DataFrame:
    """
    모든 종목의 분봉 데이터를 반환합니다.

    Args:
        time (dtm.datetime): 조회할 시간
        include_empty (bool): 거래가 없는 종목 데이터도 포함할지 여부 (기본값: False)

    Returns:
        pd.DataFrame: 요청한 시간의 모든 종목의 분봉 데이터를 담은 DataFrame

        - code (str): 종목 코드
        - time (dtm.datetime): 시간
        - open (int): 시가
        - high (int): 고가
        - low (int): 저가
        - close (int): 종가
        - volume (int): 거래량

    Examples:
        >>> df = get_all_minute_data(dtm.datetime(2024, 4, 2, 13, 0))
        >>> print(df)
                                time    open    high     low   close  volume
        code
        310210 2024-04-02 13:00:00   33400   33450   33400   33450      11
        000270 2024-04-02 13:00:00  104300  104500  104300  104500    7386
        359090 2024-04-02 13:00:00    1449    1456    1447    1451   21871
        003670 2024-04-02 13:00:00  288000  288000  287500  288000      91
        028300 2024-04-02 13:00:00  100400  100500  100300  100500    4701
        ...                    ...     ...     ...     ...     ...     ...
        002600 2024-04-02 13:00:00  171900  171900  171900  171900       1
        001725 2024-04-02 13:00:00   63400   63400   63400   63400      83
        005745 2024-04-02 13:00:00    9770    9770    9770    9770     400
        032685 2024-04-02 13:00:00   10090   10090   10090   10090      12
        003075 2024-04-02 13:00:00   13790   13790   13790   13790       1
        [1981 rows x 6 columns]

    """
    tz = pytz.timezone("Asia/Seoul")

    url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/minutes/all/{time.date()}/{time.strftime('%H%M')}"
    if include_empty:
        url += "?includeEmpty=true"

    r = requests.get(url, headers={"Authorization": f"Bearer {pyqqq.get_api_key()}"})
    if r.status_code != 200 and r.status_code != 201:
        logger.error(f"Failed to get minute data: {r.text}")
        return

    rows = r.json()
    for data in rows:
        time = data["time"].replace("Z", "+00:00")
        time = dtm.datetime.fromisoformat(time).astimezone(tz).replace(tzinfo=None)
        data["time"] = time

    df = pd.DataFrame(rows)
    if not df.empty:
        df.set_index("code", inplace=True)

    return df


def get_all_day_data(
    date: dtm.date, codes: list[str] = None
) -> dict[str, pd.DataFrame]:
    """
    지정된 날짜에 대해 하나 이상의 주식 코드에 대한 전체 분별 OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터를 검색하여 반환합니다.

    Args:
        date (dtm.date): 데이터를 검색할 날짜.
        codes (list[str], optional): 조회할 주식 코드들의 리스트. 기본값은 None이며, 이 경우 모든 주식 코드에 대한 데이터가 조회됩니다.

    Returns:
        dict[str, pd.DataFrame]: 주식 코드를 키로 하고, 해당 주식의 일일 OHLCV 데이터가 포함된 pandas DataFrame을 값으로 하는 딕셔너리.
        각 DataFrame에는 변환된 'time' 열이 포함되어 있으며, 이는 조회된 데이터의 시간을 나타냅니다. 'code' 열은 DataFrame의 인덱스로 설정됩니다.

    Raises:
        requests.exceptions.RequestException: PYQQQ API로부터 데이터를 검색하는 과정에서 오류가 발생한 경우.

    Examples:
        >>> result = get_all_day_data(dtm.date(2024, 4, 2))
        >>> len(result.keys())
        3703
        >>> print(result["069500"])
                            time   open   high    low  close  volume
        code
        069500 2024-04-02 08:31:00  37975  37975  37975  37975       1
        069500 2024-04-02 08:34:00  37975  37975  37975  37975     139
        069500 2024-04-02 08:35:00  37975  37975  37975  37975      31
        069500 2024-04-02 09:00:00  37950  37950  37905  37915   41852
        069500 2024-04-02 09:01:00  37970  37990  37950  37975   34895
        ...                    ...    ...    ...    ...    ...     ...
        069500 2024-04-02 17:10:00  38095  38095  38095  38095    1000
        069500 2024-04-02 17:20:00  38100  38100  38100  38100    3937
        069500 2024-04-02 17:40:00  38100  38100  38100  38100    1015
        069500 2024-04-02 17:50:00  38090  38090  38090  38090     145
        069500 2024-04-02 18:00:00  38100  38100  38100  38100     510
        [398 rows x 6 columns]
    """
    assert isinstance(date, dtm.date), "date must be a datetime.date object"
    if codes:
        assert isinstance(codes, list), "codes must be a list of strings"
        assert all(
            isinstance(code, str) for code in codes
        ), "codes must be a list of strings"

    tz = pytz.timezone("Asia/Seoul")

    url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/minutes/{date}"

    r = requests.get(
        url,
        headers={"Authorization": f"Bearer {pyqqq.get_api_key()}"},
        params={"codes": ",".join(codes) if codes else None},
    )

    if r.status_code != 200 and r.status_code != 201:
        logger.error(f"Failed to get day data: {r.text}")
        r.raise_for_status()

    entries = r.json()
    result = {}

    for entry in entries:
        code = entry["code"]
        rows = entry["data"]

        for row in rows:
            time = row["time"].replace("Z", "+00:00")
            time = dtm.datetime.fromisoformat(time).astimezone(tz).replace(tzinfo=None)
            row["time"] = time

        rows.reverse()

        df = pd.DataFrame(rows)
        if not df.empty:
            df.set_index("code", inplace=True)

        result[code] = df

    return result
