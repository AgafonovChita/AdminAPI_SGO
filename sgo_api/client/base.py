from aiohttp import ClientSession, ClientTimeout
from hashlib import md5
from sgo_api.log.loggers import base_logger
from sgo_api import exceptions


class BaseClient:
    def __init__(self, url: str):
        self.url = url.rstrip('/')

        self.client = ClientSession(
            base_url=f"{self.url}",
            headers={'user-agent': 'sgo_api', 'referer': self.url},
            timeout=ClientTimeout(connect=60, sock_read=None))

        self.at = None
        self.lt = None
        self.ver = None

        self.user_id = None
        self.user_name = None

        self.school_info = None
        self.school_id = None
        self.school_name = None

        self.year_id = None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.post('/asp/logout.asp',
                               data={"at": self.at, "ver": self.ver})
        await self.client.close()
        base_logger.info(f"Session is closed. User: {self.user_name} - userID: {self.user_id}")

    async def __aenter__(self) -> "BaseClient instance":
        base_logger.info(f"Session connected")
        return self

    async def force_logout(self):
        """Метод для принудительно разрыва сессии с СГО
        и закрытия клиента"""
        await self.client.post('/asp/logout.asp')
        await self.client.close()

    async def login(self, username: str, password: str, school_id: int):
        await self.client.get("/webapi/login")
        response = await self.client.post('/webapi/auth/getdata')
        login_meta = await response.json()
        salt = login_meta.pop('salt')
        self.lt, self.ver = login_meta['lt'], login_meta['ver']

        encoded_password = md5(password.encode('windows-1251')).hexdigest().encode()
        pw2 = md5(salt.encode() + encoded_password).hexdigest()
        pw = pw2[: len(password)]

        school_info = await self.get_school_data(school_id)
        self.school_info, self.school_name = school_info, school_info["sn"]

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
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) "
                              "Chrome/94.0.4606.81 Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "keep-alive"
            }
        )

        auth_data = await response.json()

        self.client.headers['AT'], self.at = auth_data['at'], auth_data['at']

        self.user_id = auth_data['accountInfo']['user']['id']
        self.user_name = auth_data['accountInfo']['user']['name']

        self.school_id = school_id

        response = await self.client.get('/webapi/years/current')
        year_info = await response.json()
        self.year_id = year_info['id']

        print(f"{self.user_name} : {self.user_id}")

    async def get_school_data(self, school_id: int):
        response = await self.client.get(
            '/webapi/addresses/schools', params={"id": school_id}
        )
        school = await response.json()
        try:
            school = school[0]
            return {
                "cid": school["countryId"],
                "sid": school["stateId"],
                "pid": school["municipalityDistrictId"],
                "cn": school["cityId"],
                "sft": 2,
                "scid": school["id"],
                "sn": school["name"]}
        except IndexError:
            await self.force_logout()
            raise exceptions.SchoolNotFoundError(self.url, school_id) from None



