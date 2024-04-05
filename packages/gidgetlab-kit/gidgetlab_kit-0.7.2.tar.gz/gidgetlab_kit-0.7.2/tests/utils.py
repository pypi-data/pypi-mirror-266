"""Utilities for tests"""

import json
import urllib
import pathlib

SAMPLES_PATH = pathlib.Path(__file__).parent / "samples"


def sample(name):
    file_path = SAMPLES_PATH / name
    with file_path.open("r") as f:
        data = json.load(f)
    return data


class FakeClient:
    async def aclose(self) -> None:
        pass


class FakeGitLab:
    def __init__(
        self, *, getiter=None, getitem=None, getitems=None, post=None, put=None
    ):
        self._getitem_return = getitems or [getitem]
        self._getiter_return = getiter
        self._post_return = post
        self._put_return = put
        self._getitem_url = []
        self.getiter_url = []
        self.post_url = []
        self.post_data = []
        self.post_params = []
        self.put_url = []
        self.put_data = []
        self.params = {}
        self.getitem_calls = 0
        self.getiter_calls = 0
        self._client = FakeClient()

    @property
    def getitem_url(self):
        if len(self._getitem_url) == 1:
            return self._getitem_url[0]
        return self._getitem_url

    async def getitem(self, url, params=None):
        self.getitem_calls += 1
        self._getitem_url.append(url)
        if params:
            self._getitem_url[-1] += f"?{urllib.parse.urlencode(params)}"
        return self._getitem_return[self.getitem_calls - 1]

    async def getiter(self, url, params=None):
        if params is None:
            params = {}
        self.params = params
        self.getiter_url.append(url)
        if self._getiter_return and isinstance(self._getiter_return[0], (list, tuple)):
            items = self._getiter_return[self.getiter_calls]
        else:
            items = self._getiter_return
        self.getiter_calls += 1
        for item in items:
            yield item

    async def post(self, url, *, data, params=None):
        if params is None:
            params = {}
        self.post_url.append(url)
        self.post_data.append(data)
        self.post_params.append(params)
        return self._post_return

    async def put(self, url, *, data):
        self.put_url.append(url)
        self.put_data.append(data)
        return self._put_return

    async def sleep(self, seconds):
        return None
