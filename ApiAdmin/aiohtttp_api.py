from aiohttp import ClientSession, ClientTimeout
from hashlib import md5
from typing import Dict


timeout = ClientTimeout(connect=60, sock_read=None)

class API:
    def __init__(self, url: str):
        url = url.rstrip('/')
        self.client = ClientSession(
            base_url=f"{url}",
            headers={'user-agent': 'ApiSGO', 'referer': url},
            timeout=timeout

        )

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

    async def __aenter__(self):
        return self

    async def logout(self):
        await self.client.post('/asp/logout.asp',
                               data={"at": self.at} )
        await self.client.close()

    async def login(self, username: str, password: str, school_id: int = 690, ):
        self.school_id = school_id
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

        self.access_token = auth_data['accessToken']
        self.refresh_token = auth_data['refreshToken']

        response = await self.client.get('/webapi/years/current')
        year_reference = await response.json()
        self.year_id = year_reference['id']

        print(f"ФИО:{self.user_name}\nID:{self.user_id}")

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
            'sn': school['name']
        }

    async def get_report_teacher_average_mark(self):
        """
        Получаем отчёт "Средний балл учителя"
        Post-data params:
        "TID" - id учителя
        "TERMID" - временной промежуток
            ( -1 это "год", -2 это "итог"(но его может не быть), можно явно указать id четверть/полугодие)
        "SJID" - предмет (-1 это "все предметы", но можно явно указать ID предмета(хз, где достать)

        :return: html-text + css-text (чтобы потом обработать и сохранить как картинку)
        """
        await self.client.post(
            url="/asp/Reports/ReportTeacherAverageMark.asp",
            data={
                'at': self.at,
                'RPNAME': 'Средний балл учителя',
                'RPTID': 'TeacherAverageMark',
                'TERMID': -2,
                'TID': self.user_id,
                # 'SJID': -1
            }
        )

        response = await self.client.post(
            url='/asp/Reports/TeacherAverageMark.asp',
            data={
                'at': self.at,
            }
        )

        response_file = await self.client.get('/static/dist/pages/common/css/export-tables.min.css')
        return await response.text(), await response_file.text()


    async def get_report_class_subject_totals(self):
        """
        Получаем отчёт "Отчёт учителя предметника"
        Post-data params:
        "TID" - id учителя
        "SJID" - предмет (-1 это "все предметы", но можно явно указать ID предмета(хз, где достать)

        :return: html-text + css-text (чтобы потом обработать и сохранить как картинку)
        """
        response = await self.client.post(
            url="/asp/Reports/ReportClassSubjectTotals.asp",
            data={
                'at': self.at,
                'ver': self.ver,
                'RPNAME': 'Отчет учителя-предметника',
                'RPTID': 'ClassSubjectTotals',
                'SJID': -1,
                'kMark_2_str': 'kHide',
                'strViewType': 'kCommonType',
                'TID': self.user_id
            }
        )

        response = await self.client.post(
            url='/asp/Reports/ClassSubjectTotals.asp',
            data={
                'at': self.at,
            }
        )

        response_file = await self.client.get('/static/dist/pages/common/css/export-tables.min.css')
        return await response.text(), await response_file.text()




