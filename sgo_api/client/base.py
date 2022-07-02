from aiohttp import ClientSession, ClientTimeout
from hashlib import md5
from typing import Union
from typing import Dict


timeout = ClientTimeout(connect=60, sock_read=None)


class BaseClient:
    def __init__(self, url: str):
        self.client: ClientSession = None

        self.url = url.rstrip('/')

        self.at = None
        self.lt = None
        self.ver = None

        self.user_id = None
        self.user_name = None

        self.access_token = None
        self.refresh_token = None

        self.school_info = None
        self.school_id = None
        self.school_name = None
        self.year_id = None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()

    async def __aenter__(self) -> ClientSession:
        self.client = ClientSession(
            base_url=f"{self.url}",
            headers={'user-agent': 'sgo_api', 'referer': self.url},
            timeout=timeout)
        return self.client

    async def logout(self):
        await self.client.post('/asp/logout.asp')
        await self.client.close()

    async def login(self, username: str, password: str, school_id: int):
        await self.client.get("/webapi/login")
        response = await self.client.post('/webapi/auth/getdata')
        login_meta = await response.json()
        salt = login_meta.pop('salt')
        self.lt = login_meta['lt']
        self.ver = login_meta['ver']

        encoded_password = md5(password.encode('windows-1251')).hexdigest().encode()
        pw2 = md5(salt.encode() + encoded_password).hexdigest()
        pw = pw2[: len(password)]

        school_info = await self.get_school_data(school_id)
        self.school_name = school_info["sn"]
        self.school_info = school_info

        response = await self.client.post(
            '/webapi/login',
            data={
                'loginType': 1,
                **school_info,
                'un': username,
                'pw': pw,
                'pw2': pw2,
                'ver': self.ver,
                'lt': self.lt,
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "keep-alive"
            }
        )

        auth_data = await response.json()

        self.client.headers['AT'] = auth_data['at']
        self.at = auth_data['at']

        self.user_id = auth_data['accountInfo']['user']['id']
        self.user_name = auth_data['accountInfo']['user']['name']
        self.school_id = school_id

        response = await self.client.get('/webapi/years/current')
        year_reference = await response.json()
        self.year_id = year_reference['id']

    async def get_school_data(self, school_id: int):
        response = await self.client.get(
            '/webapi/addresses/schools', params={"id": school_id}
        )
        school = await response.json()
        school = school[0]
        return {
            'cid': school['countryId'],
            'sid': school['stateId'],
            'pid': school['municipalityDistrictId'],
            'cn': school['cityId'],
            'sft': 2,
            'scid': school['id'],
            'sn': school['name']}


