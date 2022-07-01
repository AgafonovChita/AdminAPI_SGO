from hashlib import md5
from typing import Dict
from httpx import AsyncClient, Timeout


timeout = Timeout(10.0, connect=60.0, read=None)

class API:
    def __init__(self, url: str):
        url = url.rstrip('/')
        self.client = AsyncClient(
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
        await self.close()

    async def logout(self):
        await self.client.post('/asp/logout.asp',
                               data={
                                   "at": self.at,
                                   "VER": self.ver
                               }
                               )
        await self.client.aclose()

    async def login(self, username: str, password: str, school_id: int = 690):
        self.school_id = school_id

        response_with_cookies = await self.client.get("/webapi/logindata")
        self.client.cookies.extract_cookies(response_with_cookies)

        response = await self.client.post('/webapi/auth/getdata')
        self.client.cookies.extract_cookies(response)

        login_meta = response.json()

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
                'lt': self.lt
            }
        )

        self.client.cookies.extract_cookies(response)

        auth_data = response.json()

        self.client.headers['at'] = auth_data['at']
        self.at = auth_data['at']

        self.user_id = auth_data['accountInfo']['user']['id']
        self.user_name = auth_data['accountInfo']['user']['name']
        print(self.user_name)
        self.access_token = auth_data['accessToken']
        self.refresh_token = auth_data['refreshToken']

        # response = await self.client.post(
        #     url="/angular/school/announcements/",
        #     data={
        #         'LoginType': 0,
        #         'at': self.at,
        #         'VER': self.ver,
        #     }
        # )
        # self.client.cookies.extract_cookies(response)

    async def get_school_data(self, school_id: int) -> Dict[str, int]:
        response = await self.client.get(
            '/webapi/addresses/schools', params={"id": school_id}
        )

        school = response.json()
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
                #'SJID': -1
            }
        )

        response = await self.client.post(
            url='/asp/Reports/TeacherAverageMark.asp',
            data={
                'at': self.at,
            }
        )

        response_file = await self.client.get('/static/dist/pages/common/css/export-tables.min.css')
        return response.text, response_file.text


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
        return response.text, response_file.text

    async def get_stuff(self):
        """Получить список всех сотрудников"""
        try:
            response = await self.client.post(
                url="/angular/school/users/staff/",
                data={
                    'LoginType': 0,
                    'at': self.at,
                    'ver': self.ver,
                }
            )

            response = await self.client.get(
                url="/webapi/appflags/persondata",
            )


            response = await self.client.post(
                url="/webapi/users/staff/registry",
                data={
                    "fields": ["fio"],
                    "page": 1,
                    "pageSize": 200,
                    "order": {
                        "fieldId": "fio",
                        "ascending": True
                    }
                }

            )

            print(response.json())
            response_file = await self.client.get('/static/dist/pages/common/css/export-tables.min.css')
            return response.text, response_file.text

        except Exception as e:
            print(f"Я помер, потому что: {e}")
            self.logout()


