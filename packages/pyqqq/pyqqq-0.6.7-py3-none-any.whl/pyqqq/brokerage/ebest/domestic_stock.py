from pyqqq.brokerage.ebest.oauth import EBestAuth
from pyqqq.brokerage.ebest.tr_client import (
    EBestTRClient,
    EBestTRWebsocketClient,
    EBestTRWebsocketKeepConnectionStatus,
)
from pyqqq.utils.limiter import limit_calls
from typing import AsyncGenerator
import asyncio
import datetime as dtm
import json
import websockets

from pyqqq.utils.market_schedule import get_market_schedule


class EBestDomesticStock:
    """
    이베스트투자증권 국내주식 API
    """

    def __init__(self, auth: EBestAuth, corp_data: dict = None):
        self.auth = auth
        self.corp_data = corp_data
        self.tr_client = EBestTRClient(auth)

    def _tr_request(self, *args, **kwargs):
        return self.tr_client.request(*args, **kwargs)

    @limit_calls(scope="ebest/t8436", max_calls=2)
    def get_asset_list(self, market_type: str = "0") -> list:
        """
        ([주식]기타) 주식종목조회 API용 (t8436)

        Args:
            market_type (str): 시장유형 (0:전체 1:코스피 2:코스닥)

        Returns:
            dict:

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output (list): 주식 종목 리스트

                - hname (str): 종목명
                - shcode (str): 단축코드
                - expcode (str): 확장코드
                - etfgubun (str): ETF구분 (0:일반 1:ETF 2:ETN)
                - uplmtprice (float): 상한가
                - dnlmtprice (float): 하한가
                - jnilclose (float): 전일종가
                - memedan (float): 주문수량단위
                - recprice (int): 기준가
                - gubun (str): 구분 (1:코스피 2:코스닥)
                - bu12gubun (str): 12월결산월
                - spac_gubun (str): 기업인수목적회사여부 (Y:기업인수목적회사)
                - filler (str): filler
        """

        assert market_type in ["0", "1", "2"], "Invalid market type"

        tr_code = "t8436"
        req_body = {f"{tr_code}InBlock": {"gubun": market_type}}

        res_body, _ = self._tr_request("/stock/etc", tr_code, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output": res_body.get("t8436OutBlock", []),
        }

        return result

    @limit_calls(scope="ebest/t1102", max_calls=3)
    def get_price(self, asset_code: str) -> dict:
        """
        ([주식]시세) 주식현재가(시세)조회 (t1102)

        Args:
            asset_code (str): 종목 코드

        Returns:
            dict: 종목의 현재가 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output (list): 종목의 현재가 정보
        """
        assert len(asset_code) == 6, "Invalid asset code"

        tr_code = "t1102"
        req_body = {f"{tr_code}InBlock": {"shcode": asset_code}}
        res_body, _ = self._tr_request("/stock/market-data", tr_code, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output": res_body.get("t1102OutBlock", []),
        }

        return result

    @limit_calls(scope="ebest/t1301", max_calls=2)
    def get_stock_time_conclude(
        self,
        asset_code: str,
        cvolume: int,
        start_time: dtm.time,
        end_time: dtm.time,
        cts_time: str = "",
        tr_cont_key: str = "",
    ) -> dict:
        """
        ([주식]시세) 주식시간대별체결조회 (t1301)

        Args:
            asset_code (str): 종목 코드
            cvolume (int): 특이거래량
            start_time (dtm.time): 시작시간 - 장시작시간 이후
            end_time (dtm.time): 종료시간 - 장종료시간 이전
            cts_time (str): 연속시간 - 연속조회시 OutBlock의 동일필드 입력

        Returns:
            dict: 주식 시간대별 체결 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output (list): 주식 시간대별 체결 정보
        """

        assert len(asset_code) == 6, "Invalid asset code"

        tr_code = "t1301"
        tr_cont = "Y" if cts_time else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "shcode": asset_code,
                "cvolume": cvolume,
                "starttime": start_time.strftime("%H%M"),
                "endtime": end_time.strftime("%H%M"),
                "cts_time": cts_time,
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/market-data",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output": res_body.get("t1301OutBlock", []),
        }

        return result

    @limit_calls(scope="ebest/t1302", max_calls=1)
    def get_stock_minute_prices(
        self,
        shcode: str,
        gubun: str,
        cnt=900,
        cts_time: str = "",
        tr_cont_key: str = "",
    ):
        """
        ([주식]시세) 주식분별주가조회 (t1302)

        Args:
            shcode (str): 종목 코드
            gubun (str): 주기구분 (1:1분 2:3분 3:5분 4:10분 5:30분 6:60분)
            cnt (int): 조회건수 - 최대 900
            cts_time (str): 연속시간 - 연속조회시 OutBlock의 동일필드 입력
            tr_cont_key (str): 연속조회키 - 연속조회시 이전 응답 헤더의 동일필드 입력

        Returns:
            dict: 주식 분별 주가 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 연속 조회를 위한 cts_time 필드를 포함
            - output2 (list): 주식 분별 주가 정보
        """

        assert len(shcode) == 6, "Invalid asset code"
        assert gubun in ["1", "2", "3", "4", "5", "6"], "Invalid gubun"

        tr_code = "t1302"
        tr_cont = "Y" if cts_time else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "shcode": shcode,
                "gubun": gubun,
                "cnt": cnt,
                "cts_time": cts_time,
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/market-data",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": res_body.get("t1302OutBlock", {}),
            "output2": res_body.get("t1302OutBlock1", []),
        }

        return result

    @limit_calls(scope="ebest/t1310", max_calls=1)
    def get_stock_tick_data_today_yesterday(
        self,
        daygb: int,
        timegb: int,
        shcode: str,
        endtime: dtm.time,
        cts_time: str = "",
        tr_cont_key: str = "",
    ):
        """
        ([주식]시세) 주일당일전일분틱조회 (t1310)

        Args:
            daygb (int): 일자구분 (0:당일 1:전일)
            timegb (int): 시간구분 (0:분 1:틱)
            shcode (str): 종목 코드
            endtime (dtm.time): 종료시간 outblock.chetime <= endtime 인 데이터 조회됨
            cts_time (str): 연속시간 - 연속조회시 OutBlock의 동일필드 입력
            tr_cont_key (str): 연속조회키 - 연속조회시 이전 응답 헤더의 동일필드 입력

        Returns:
            dict: 응답 데이터

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 연속 조회를 위한 cts_time 필드를 포함
            - output2 (list): 분틱 정보
        """
        assert daygb in [0, 1], "Invalid daygb"
        assert timegb in [0, 1], "Invalid timegb"
        assert len(shcode) >= 6, "Invalid asset code"
        assert isinstance(endtime, dtm.time), "Invalid endtime"

        tr_code = "t1310"
        req_body = {
            f"{tr_code}InBlock": {
                "daygb": str(daygb),
                "timegb": str(timegb),
                "shcode": shcode,
                "endtime": endtime.strftime("%H%M"),
                "cts_time": cts_time,
            }
        }

        tr_cont = "Y" if cts_time else "N"

        res_body, res_header = self._tr_request(
            "/stock/market-data",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": res_body.get("t1310OutBlock", {}),
            "output2": res_body.get("t1310OutBlock1", []),
        }

        return result

    @limit_calls(scope="ebest/t8410", max_calls=1)
    def get_stock_chart_dwmy(
        self,
        shcode: str,
        gubun: str,
        edate: dtm.date,
        sdate: dtm.date = None,
        qrycnt: int = 500,
        cts_date: str = "",
        comp_yn: bool = False,
        sujung_yn: bool = False,
        tr_cont_key: str = "",
    ):
        """
        ([주식]차트) API전용주식챠트(일주월년) (t8410)

        Args:
            shcode (str): 종목 코드
            gubun (str): 주기구분 (d:일 w:주 m:월 y:년)
            qrycnt (int): 요청건수 (최대-압축:2000비압축:500)
            edate (dtm.date): 종료일자 - 처음조회기준일(LE) 처음 조회일 경우 이 값 기준으로 조회
            sdate (dtm.date): 시작일자 - 기본값(None)인 경우 edate 기준으로  qrycnt 만큼 조회. 조회구간을 설정하여 필터링하고 싶은 경우 입력.
            cts_date (str): 연속일자 - 연속조회시 OutBlock의 동일필드 입력
            comp_yn (bool): 압축여부 (True:압축 False:비압축)
            sujung_yn (bool): 수정주가적용여부 (True:수정주가적용 False:비적용)
            tr_cont_key (str): 연속조회키 - 연속조회시 이전 응답 헤더의 동일필드 입력

        Returns:
            dict: 주식 차트 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 전일/당일 시세 정보
            - output2 (list): 주기별 시세 정보
        """

        assert len(shcode) == 6, "Invalid asset code"
        assert gubun.lower() in ["d", "w", "m", "y"], "Invalid gubun"

        tr_code = "t8410"
        tr_cont = "Y" if cts_date else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "shcode": shcode,
                "gubun": {"d": "2", "w": "3", "m": "4", "y": "5"}[gubun.lower()],
                "qrycnt": qrycnt,
                "sdate": sdate.strftime("%Y%m%d") if sdate else "",
                "edate": edate.strftime("%Y%m%d"),
                "cts_date": cts_date,
                "comp_yn": "Y" if comp_yn else "N",
                "sujung_yn": "Y" if sujung_yn else "N",
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/chart",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get("t8410OutBlock", {}),
            "output2": res_body.get("t8410OutBlock1", []),
        }

        return result

    @limit_calls(scope="ebest/t8412", max_calls=1)
    def get_stock_chart_minutes(
        self,
        shcode: str,
        ncnt: int,
        qrycnt: int,
        nday: int,
        edate: dtm.date,
        sdate: dtm.date = None,
        cts_date: str = "",
        cts_time: str = "",
        comp_yn: bool = False,
        tr_cont_key: str = "",
    ) -> dict:
        """
        ([주식]차트) 주식분별주가조회 (t8412)

        Args:
            shcode (str): 종목 코드
            ncnt (int): 단위(n분)
            qrycnt (int): 요청건수 (최대-압축:2000비압축:500)
            nday (int): 조회영업일수(0:미사용 1>=사용)
            edate (dtm.date): 종료일자 - 처음조회기준일(LE) 처음 조회일 경우 이 값 기준으로 조회
            sdate (dtm.date): 시작일자 - 기본값(None)인 경우 edate 기준으로  qrycnt 만큼 조회. 조회구간을 설정하여 필터링하고 싶은 경우 입력.
            cts_date (str): 연속일자 - 연속조회시 OutBlock의 동일필드 입력
            cts_time (str): 연속시간 - 연속조회시 OutBlock의 동일필드 입력
            comp_yn (bool): 압축여부 (True:압축 False:비압축)
            tr_cont_key (str): 연속조회키 - 연속조회시 이전 응답 헤더의 동일필드 입력

        Returns:
            dict: 주식 차트 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 전일/당일 시세 정보
            - output2 (list): 단위 별 주식 차트 정보
        """

        tr_code = "t8412"
        tr_cont = "Y" if cts_date else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "shcode": shcode,
                "ncnt": ncnt,
                "qrycnt": qrycnt,
                "nday": str(nday),
                "sdate": sdate.strftime("%Y%m%d") if sdate else "",
                "edate": edate.strftime("%Y%m%d"),
                "cts_date": cts_date,
                "cts_time": cts_time,
                "comp_yn": "Y" if comp_yn else "N",
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/chart",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get("t8412OutBlock", {}),
            "output2": res_body.get("t8412OutBlock1", []),
        }

        return result

    @limit_calls(scope="ebest/CSPAQ12200", max_calls=1)
    def get_account_deposit_orderable_total_evaluation(self) -> dict:
        """
        ([주식]계좌) 현물계좌예수금 주문가능금액 총평가 조회 (CSPAQ12200)

        Returns:
            dict: 주문가능금액 총평가 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output1 (dict): 계좌기본정보
            - output2 (dict): 주문가능금액 총평가 정보
        """

        tr_code = "CSPAQ12200"
        req_body = {f"{tr_code}InBlock1": {"BalCreTp": "0"}}

        res_body, _ = self._tr_request("/stock/accno", tr_code, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get("CSPAQ12200OutBlock1", {}),
            "output2": res_body.get("CSPAQ12200OutBlock2", {}),
        }

        return result

    @limit_calls(scope="ebest/CSPBQ00200", max_calls=1)
    def get_account_orderable_quantity(
        self,
        bns_tp_code: int,
        isu_no: str,
        ord_prc: int,
    ) -> dict:
        """
        ([주식]계좌) 현물계좌증거금률별주문가능수량조회 (CSPBQ00200)

        Args:
            bns_tp_code (int): 매매구분 (1:매도 2:매수)
            isu_no (str): 종목번호
            ord_prc (int): 주문가격

        Returns:
            dict: 주문가능수량 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output1 (dict): 요청 정보
            - output2 (dict): 계좌 및 증거금률 별 주문가능수량 정보
        """
        assert bns_tp_code in [1, 2], "Invalid bns_tp_code"
        assert len(isu_no) == 6 or (
            len(isu_no) == 7 and isu_no[0] == "A"
        ), "Invalid isu_no"

        tr_code = "CSPBQ00200"
        req_body = {
            f"{tr_code}InBlock1": {
                "BnsTpCode": str(bns_tp_code),
                "IsuNo": "A" + isu_no if len(isu_no) == 6 else isu_no,
                "OrdPrc": ord_prc,
            }
        }

        res_body, _ = self._tr_request("/stock/accno", tr_code, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get("CSPBQ00200OutBlock1", {}),
            "output2": res_body.get("CSPBQ00200OutBlock2", {}),
        }

        return result

    @limit_calls(scope="ebest/t0424", max_calls=1)
    def get_stock_balance(
        self,
        prcgb: int = 1,
        chegb: int = 0,
        dangb: int = 0,
        charge: int = 0,
        cts_expcode: str = "",
        tr_cont_key: str = "",
    ):
        """
        ([주식]계좌) 주식잔고2조회 (t0424)

        Args:
            prcgb (int): 단가구분 (1:평균단가, 2:BEP단가)
            chegb (int): 체결구분 (0:결제기준잔고, 2:체결기준(잔고가 0이 아닌 종목만 조회)
            dangb (int): 단일가구분 (0:정규장, 1:시장외단일가)
            charge (int): 수수료구분 (0:제비용미포함, 1:제비용포함)
            cts_expcode (str): 연속종목코드 - 연속조회시 OutBlock의 동일필드 입력

        Returns:
            dict: 주식 잔고 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 계좌 정보
            - output2 (list): 종목 별 잔고 정보
        """

        assert prcgb in [1, 2], "Invalid prcgb"
        assert chegb in [0, 2], "Invalid chegb"
        assert dangb in [0, 1], "Invalid dangb"
        assert charge in [0, 1], "Invalid charge"

        tr_code = "t0424"
        tr_cont = "Y" if cts_expcode else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "prcgb": str(prcgb),
                "chegb": str(chegb),
                "dangb": str(dangb),
                "charge": str(charge),
                "cts_expcode": cts_expcode,
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/accno",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get("t0424OutBlock", []),
            "output2": res_body.get("t0424OutBlock1", []),
        }

        return result

    @limit_calls(scope="ebest/CSPAQ13700", max_calls=1)
    def get_deposit_order_list(
        self,
        isu_no: str = "",
        ord_mkt_code: str = "00",
        bns_tp_code: str = "0",
        exec_yn: str = "0",
        ord_dt: str = None,
        srt_ord_no2: str = "999999999",
        bkseq_tp_code: str = "0",
        ord_ptn_code: str = "00",
    ) -> dict:
        """
        ([주식]계좌) 현물계좌 주문체결내역 조회(API) (CSPAQ13700)
        """
        tr_code = "CSPAQ13700"
        if ord_dt is None:
            ord_dt = dtm.date.today().strftime("%Y%m%d")

        req_body = {
            f"{tr_code}InBlock1": {
                "IsuNo": isu_no,
                "OrdMktCode": ord_mkt_code,
                "BnsTpCode": bns_tp_code,
                "ExecYn": exec_yn,
                "OrdDt": ord_dt,
                "SrtOrdNo2": int(srt_ord_no2),
                "BkseqTpCode": bkseq_tp_code,
                "OrdPtnCode": ord_ptn_code,
            }
        }

        res_body, res_header = self._tr_request("/stock/accno", tr_code, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": res_body.get("CSPAQ13700OutBlock1", {}),
            "output2": res_body.get("CSPAQ13700OutBlock2", {}),
            "output3": res_body.get("CSPAQ13700OutBlock3", {}),
        }

        return result

    @limit_calls(scope="ebest/t0425", max_calls=1)
    def get_order_list(
        self,
        chegb: int = 0,
        medosu: int = 0,
        sortgb: int = 2,
        expcode: str = "",
        cts_ordno: str = "",
        tr_cont_key: str = "",
    ) -> dict:
        """
        ([주식]계좌) 주식체결/미체결 (t0425)

        Args:
            chegb (int): 체결구분 (0:전체, 1:체결, 2:미체결)
            medosu (int): 매도수구분 (0:전체, 1:매도, 2:매수)
            sortgb (int): 정렬기준 (1:주문번호 역순, 2:주문번호 순)
            expcode (str): 종목코드. 전체조회 시 입력값 없음
            cts_ordno (str): 연속주문번호 - 연속조회시 OutBlock의 동일필드 입력
            tr_cont_key (str): 연속조회키 - 연속조회시 이전 응답 헤더의 동일필드 입력

        Returns:
            dict: 주식 체결/미체결 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 총 주문/체결 정보
            - output2 (list): 주문 별 정보
        """
        tr_code = "t0425"
        tr_cont = "Y" if cts_ordno else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "chegb": str(chegb),
                "medosu": str(medosu),
                "sortgb": str(sortgb),
                "expcode": expcode,
                "cts_ordno": cts_ordno,
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/accno",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        res_body.update(
            {
                "tr_cont": res_header.get("tr_cont", ""),
                "tr_cont_key": res_header.get("tr_cont_key", ""),
            }
        )

        if "t0425OutBlock" not in res_body:
            res_body["t0425OutBlock"] = {
                "tqty": 0,
                "tcheqty": 0,
                "tordrem": 0,
                "cmss": 0,
                "tamt": 0,
                "tmdamt": 0,
                "tmsamt": 0,
                "tax": 0,
                "cts_ordno": "",
            }

        if "t0425OutBlock1" not in res_body:
            res_body["t0425OutBlock1"] = []

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": res_body["t0425OutBlock"],
            "output2": res_body["t0425OutBlock1"],
        }

        return result

    @limit_calls(scope="ebest/CSPAT00601", max_calls=10)
    def create_order(
        self,
        isu_no: str,
        ord_qty: int,
        ord_prc: int,
        bns_tp_code: int,
        ord_prc_ptn_code: str,
        mgntrn_code: str = "000",
        load_dt: dtm.date = None,
        ord_cndi_tp_code: int = "0",
    ) -> dict:
        """
        ([주식]주문) 현물주문 (CSPAT00601)

        Args:
            isu_no (str): 종목번호

                | 주식/ETF: (종목코드) or A+종목코드
                | ELW: J+종목코드
                | ETN: Q+종목코드

            ord_qty (int): 주문수량
            ord_prc (int): 주문가격
            bns_tp_code (int): 매매구분 (1:매도 2:매수)
            ord_prc_ptn_code (str): 호가유형코드

                | '00: 지정가
                | '03': 시장가
                | '05': 조건부지정가
                | '06': 최유리지정가
                | '07': 최우선지정가
                | '61': 장개시전시간외종가
                | '81': 시간외단일가매매
                | '82': 시간외종가

            mgntrn_code (str): 신용거래코드

                | '000': 보통
                | '003': 유통/자기융자신규
                | '005': 유통대주신규
                | '007': 자기대주신규
                | '101': 유통융자상환
                | '103': 자기융자상환
                | '105': 유통대주상환
                | '107': 자기대주상환
                | '180': 유통대주주문취소

            load_dt (dtm.date): 대출일
            ord_cndi_tp_code (int): 주문조건구분 (0:없음 1:IOC 2:FOK)

        Returns:
            dict: 주문 결과

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output1 (dict): 주문 결과
            - output2 (dict): 주문 결과
        """
        tr_cd = "CSPAT00601"
        req_body = {
            f"{tr_cd}InBlock1": {
                "IsuNo": isu_no,
                "OrdQty": ord_qty,
                "OrdPrc": ord_prc,
                "BnsTpCode": str(bns_tp_code),
                "OrdprcPtnCode": ord_prc_ptn_code,
                "MgntrnCode": mgntrn_code,
                "LoanDt": load_dt.strftime("%Y%m%d") if load_dt else "",
                "OrdCndiTpCode": str(ord_cndi_tp_code),
            }
        }

        res_body, _ = self._tr_request("/stock/order", tr_cd, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get(f"{tr_cd}OutBlock1", {}),
            "output2": res_body.get(f"{tr_cd}OutBlock2", {}),
        }

        return result

    @limit_calls(scope="ebest/CSPAT00701", max_calls=3)
    def update_order(
        self,
        org_ord_no: str,
        isu_no: str,
        ord_qty: int,
        ord_prc_ptn_code: str,
        ord_cndi_tp_code: int = 0,
        ord_prc: int = 0,
    ) -> dict:
        """
        ([주식]주문) 현물정정주문 (CSPAT00701)

        Args:
            org_ord_no (str): 원주문번호
            isu_no (str): 종목번호
            ord_qty (int): 주문수량
            ord_prc_ptn_code (str): 호가유형코드

                | '00: 지정가
                | '03': 시장가
                | '05': 조건부지정가
                | '06': 최유리지정가
                | '07': 최우선지정가
                | '61': 장개시전시간외종가
                | '81': 시간외단일가매매
                | '82': 시간외종가

            ord_cndi_tp_code (int): 주문조건구분 (0:없음 1:IOC 2:FOK)
            ord_prc (int): 주문가격

        Returns:
            dict: 주문 결과

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output1 (dict): 원 주문 정보
            - output2 (dict): 정정 주문 정보
        """

        tr_cd = "CSPAT00701"
        req_body = {
            f"{tr_cd}InBlock1": {
                "OrgOrdNo": int(org_ord_no),
                "IsuNo": isu_no,
                "OrdQty": ord_qty,
                "OrdprcPtnCode": ord_prc_ptn_code,
                "OrdCndiTpCode": str(ord_cndi_tp_code),
                "OrdPrc": ord_prc,
            }
        }

        res_body, _ = self._tr_request("/stock/order", tr_cd, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get(f"{tr_cd}OutBlock1", {}),
            "output2": res_body.get(f"{tr_cd}OutBlock2", {}),
        }

        return result

    @limit_calls(scope="ebest/CSPAT00801", max_calls=3)
    def cancel_order(self, org_ord_no: str, isu_no: str, ord_qty: int) -> dict:
        """
        ([주식]주문) 현물취소주문 (CSPAT00801)

        Args:
            org_ord_no (str): 원주문번호
            isu_no (str): 종목번호
            ord_qty (int): 주문수량

        Returns:
            dict: 주문 결과

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output1 (dict): 원 주문 정보
            - output2 (dict): 취소 주문 정보

        """

        tr_cd = "CSPAT00801"
        req_body = {
            f"{tr_cd}InBlock1": {
                "OrgOrdNo": int(org_ord_no),
                "IsuNo": isu_no,
                "OrdQty": ord_qty,
            }
        }

        res_body, _ = self._tr_request("/stock/order", tr_cd, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get(f"{tr_cd}OutBlock1", []),
            "output2": res_body.get(f"{tr_cd}OutBlock2", []),
        }

        return result

    def get_management_stocks(
        self, gubun: str, jongchk: str, cts_shcode: str = "", tr_cont_key: str = ""
    ):
        """
        ([주식]시세) 관리/불성실/투자유의조회 (t1404)

        Args:
            gubun (str): 구분 (0:전체 1:코스피 2:코스닥)
            jongchk (str): 종목체크 (1:관리 2:불성실공시 3:투자유의 4.투자환기)
            cts_shcode (str): 연속종목코드 - 연속조회시 OutBlock의 동일필드 입력

        Returns:
            dict: 관리/불성실/투자유의 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 연속조회정보
            - output2 (list): 종목 별 정보
        """
        tr_cd = "t1404"
        req_body = {
            f"{tr_cd}InBlock": {
                "gubun": gubun,
                "jongchk": jongchk,
                "cts_shcode": cts_shcode,
            }
        }

        tr_cont = "Y" if cts_shcode else "N"

        res_body, _ = self._tr_request(
            "/stock/market-data", tr_cd, tr_cont, tr_cont_key, body=req_body
        )

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_body.get("tr_cont", ""),
            "tr_cont_key": res_body.get("tr_cont_key", ""),
            "output1": res_body.get("t1404OutBlock", {}),
            "output2": res_body.get("t1404OutBlock1", []),
        }

        return result

    def get_alert_stocks(
        self, gubun: str, jongchk: str, cts_shcode: str = "", tr_cont_key=""
    ):
        """
        ([주식]시세) 투자경고/매매정지/정리매매조회 (t1405)

         Args:
            gubun (str): 구분 (0:전체 1:코스피 2:코스닥)
            jongchk (str): 종목체크 (1:투자경고 2:매매정지 3:정리매매 4:투자주의 5:투자위험 6:위험예고 7:단기과열지정 8:이상급등종목 9:상장주식수부족)
            cts_shcode (str): 연속종목코드 - 연속조회시 OutBlock의 동일필드 입력

        Returns:
            dict: 투자경고/매매정지/정리매매 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 연속조회정보
            - output2 (list): 종목 별 정보

        """
        tr_cd = "t1405"
        req_body = {
            f"{tr_cd}InBlock": {
                "gubun": gubun,
                "jongchk": jongchk,
                "cts_shcode": cts_shcode,
            }
        }
        tr_cont = "Y" if cts_shcode else "N"
        res_body, res_header = self._tr_request(
            "/stock/market-data", tr_cd, tr_cont, tr_cont_key, body=req_body
        )

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": res_body.get("t1405OutBlock", {}),
            "output2": res_body.get("t1405OutBlock1", []),
        }

        return result

    async def listen_trade_event(
        self,
        market: str,
        asset_codes: list[str],
        stop_event: asyncio.Event = None,
    ) -> AsyncGenerator:
        """
        체결 이벤트를 수신합니다.
        장/전후 시간외 종가 거래에 대한 체결 이벤트를 포함합니다.

        Args:
            market (str): 시장 (1:코스피 2:코스닥)
            asset_codes (list[str]): 종목 코드 리스트
        """

        assert market in ["1", "2"], "Invalid market"
        assert type(asset_codes) == list, "Invalid asset_codes"
        assert len(asset_codes) > 0, "Invalid asset_codes"

        def __on_ask_keep_connection() -> EBestTRWebsocketKeepConnectionStatus:
            now = dtm.datetime.now()
            today = now.date()
            market_schedule = get_market_schedule(today)

            if market_schedule.full_day_closed:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            open_time = dtm.datetime.combine(today, market_schedule.open_time)
            close_time = dtm.datetime.combine(today, market_schedule.close_time)
            # 장전 시강외종가 거래 시작 시간
            pre_market_open_time = open_time - dtm.timedelta(minutes=30)
            # 장후 시간외종가 거래 종료 시간
            after_market_close_time = close_time + dtm.timedelta(minutes=30)
            time_margin = dtm.timedelta(minutes=5)

            if now < pre_market_open_time - time_margin:
                return EBestTRWebsocketKeepConnectionStatus.WAIT

            if now > after_market_close_time + time_margin:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            return EBestTRWebsocketKeepConnectionStatus.KEEP

        async def __on_connect(ws: websockets.WebSocketClientProtocol):
            for asset_code in asset_codes:
                await ws.send(
                    json.dumps(
                        {
                            "header": {
                                "token": self.auth.get_token(),
                                "tr_type": "3",
                            },
                            "body": {
                                "tr_cd": "S3_" if market == "1" else "K3_",
                                "tr_key": asset_code,
                            },
                        }
                    )
                )

                await asyncio.sleep(0.01)

        client = EBestTRWebsocketClient(
            self.auth,
            on_connect=__on_connect,
            on_ask_keep_connection=__on_ask_keep_connection,
            stop_event=stop_event,
        )

        async for data in client.listen():
            yield data

    async def listen_after_market_single_price_trade_event(
        self,
        market: str,
        asset_codes: list[str],
        stop_event: asyncio.Event = None,
    ):
        """
        시간외단일가 체결 이벤트를 수신합니다.
        장 종료 30분 후부터 2시간 동안 시간외단일가 거래가 이루어집니다. (일반적으로 16:00~18:00)

        Args:
            market (str): 시장 (1:코스피 2:코스닥)
            asset_codes (list[str]): 종목 코드 리스트
        """

        assert market in ["1", "2"], "Invalid market"
        assert type(asset_codes) == list, "Invalid asset_codes"
        assert len(asset_codes) > 0, "Invalid asset_codes"

        def __on_ask_keep_connection() -> EBestTRWebsocketKeepConnectionStatus:
            now = dtm.datetime.now()
            today = now.date()
            market_schedule = get_market_schedule(today)

            if market_schedule.full_day_closed:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            close_time = dtm.datetime.combine(today, market_schedule.close_time)

            # 장후 시간외 단일가 거래 시작 시간
            after_market_open_time = close_time + dtm.timedelta(minutes=30)
            # 장후 시간외 단일가 거래 종료 시간
            after_market_close_time = close_time + dtm.timedelta(hours=2, minutes=30)
            time_margin = dtm.timedelta(minutes=5)

            if now < after_market_open_time - time_margin:
                return EBestTRWebsocketKeepConnectionStatus.WAIT

            if now > after_market_close_time + time_margin:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            return EBestTRWebsocketKeepConnectionStatus.KEEP

        async def __on_connect(ws: websockets.WebSocketClientProtocol):
            for asset_code in asset_codes:
                await ws.send(
                    json.dumps(
                        {
                            "header": {
                                "token": self.auth.get_token(),
                                "tr_type": "3",
                            },
                            "body": {
                                "tr_cd": "DS3" if market == "1" else "DK3",
                                "tr_key": asset_code,
                            },
                        }
                    )
                )
                await asyncio.sleep(0.01)

        client = EBestTRWebsocketClient(
            self.auth,
            on_connect=__on_connect,
            on_ask_keep_connection=__on_ask_keep_connection,
            stop_event=stop_event,
        )

        async for data in client.listen():
            yield data
