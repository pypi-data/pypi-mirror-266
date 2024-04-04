from typing import List
import json
import requests
import os
import pyqqq.config as c
from pyqqq import get_api_key
from pyqqq.utils.retry import retry


class KVStore:
    """
    Simple key-value store

    Args:
        context_name (str, optional): 전략 등 DB 구분을 위한 context 식별자. 기본값은 "default".
    """

    def __init__(self, context_name: str = "default"):
        self.name = context_name

    def get(self, key: str) -> str | bool | int | float | dict | list | None:
        """
        KV store 로 부터 key 에 해당하는 값을 가져온다.

        Args:
            key (str): key

        Returns:
            str | bool | int | float | dict | list | None: value
        """
        assert type(key) == str, "key must be a string"
        assert len(key) > 0, "key must not be empty"

        url = f"{c.PYQQQ_API_URL}/kvstore/get-value"
        params = {"contextName": self.name, "key": key}
        r = self._send_request("GET", url, params=params)
        r.raise_for_status()

        if len(r.text) == 0:
            return None

        data = r.json()
        if data:
            return json.loads(data)
        else:
            return None

    def set(
        self, key: str, value: str | bool | int | float | dict | list | None
    ) -> bool:
        """
        KV store 에 key 에 해당하는 값을 저장한다.

        value는 json.dumps로 serialize 가능한 값이어야 한다.
        value가 None이면 key를 삭제한다. (delete 메소드와 동일한 효과)


        Args:
            key (str): key
            value (str | bool | int | float | dict | list | None): value

        Returns:
            bool: 성공 여부
        """
        assert type(key) == str, "key must be a string"
        assert len(key) > 0, "key must not be empty"
        assert type(value) in [
            str,
            bool,
            int,
            float,
            dict,
            list,
            None,
        ], "value must be a string, bool, int, float, dict, list, or None"

        if value is None:
            return self.delete(key)

        try:
            value = json.dumps(value)
        except:
            raise ValueError("value must be serializable to JSON")

        req_body = {
            "contextName": self.name,
            "key": key,
            "value": value,
        }

        r = self._send_request(
            "PUT", f"{c.PYQQQ_API_URL}/kvstore/set-value", json=req_body
        )
        r.raise_for_status()

        data = r.json()
        return data.get("message") == "success"

    def delete(self, key: str) -> bool:
        """
        KV store 에서 key 에 해당하는 값을 삭제한다.

        Args:
            key (str): key

        Returns:
            bool: 성공 여부
        """
        req_body = {
            "contextName": self.name,
            "key": key,
        }

        r = self._send_request(
            "DELETE", f"{c.PYQQQ_API_URL}/kvstore/delete-value", json=req_body
        )
        if r.status_code != 200:
            print(r.text)

        r.raise_for_status()

        data = r.json()
        return data.get("message") == "success"

    def keys(self) -> List[str]:
        """
        KV store 에 저장된 모든 key 를 가져온다.

        Returns:
            List[str]: key list
        """
        url = f"{c.PYQQQ_API_URL}/kvstore/list-keys"
        r = self._send_request("GET", url, params={"contextName": self.name})
        r.raise_for_status()

        data = r.json()

        return data if data else []

    @retry(requests.HTTPError)
    def _send_request(self, method: str, url: str, **kwargs):
        api_key = get_api_key()
        if not api_key:
            raise ValueError("API key is not set")

        return requests.request(
            method=method,
            url=url,
            headers={"Authorization": f"Bearer {api_key}"},
            **kwargs,
        )
