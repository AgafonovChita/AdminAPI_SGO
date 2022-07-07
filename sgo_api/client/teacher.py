from sgo_api.client.base import BaseClient
import asyncio
import time


class TeacherClient(BaseClient):
    def __init__(self, url: str):
        super().__init__(url=url)

    async def get_students_from_class(self, class_id: int = 105007):
        """
        Получаем список учащихся класса
        :param class_id: id класса (можно узнать при помощи метода get_classes)
        :return: list of dicts
        example:[{'id': 937123, 'fullName': 'Иван Иванов'}, ...]
        """
        response = await self.client.get(
            url="/webapi/grade/studentList",
            params=f"classId={class_id}"
        )
        return await response.json()


    async def get_vocations(self):
        """
        Получаем все каникулы
        :return: list dicts
        example: [{'startTime': '2021-10-25T00:00:00', 'endTime': '2021-10-31T00:00:00',
        'id': 111491, 'name': 'Осенние каникулы'}, ...]
        """
        await asyncio.sleep(10)
        response = await self.client.get(
            url="/webapi/calendar/vacations"
        )
        return await response.json()

    async def get_terms(self):
        """
        Получаем все учебные периоды
        :return: list dicts
        example: [{'id': 26904, 'termName': '1 четверть', 'termTypeId': 1,
        'startDate': '2021-09-01T00:00:00', 'endDate': '2021-10-31T00:00:00',
        'schoolYearId': 8987}, ...]
        """
        response = await self.client.get(
            url="/webapi/terms"
        )
        return await response.json()

    async def get_subjects(self):
        """
        Получаем все предметы
        :return: list dicts
        example: [{'shortName': 'Технология мальчики', 'teachers': None, 'groups': None,
        'parentSubject': None, 'subjectField': None,
        'globalSubject': {'id': 3255, 'name': 'технология (м)'},
        'order': None, 'using': False, 'usingInYear': False, 'extraCurricular': False,
        'isModular': False, 'useExemption': False, 'direction': None,
        'id': 47070, 'name': 'Технология мальчики'}, ... ]
        """
        response = await self.client.get(
            url="/webapi/subjects"
        )
        return await response.json()

    async def get_classes(self):
        """
        Получаем все данные по классам
        :return: json of jsons
        example: {step': {'id': 1, 'name': ' 1- 4 кл.'},
        'iup': False,
        'grade': {'id': 1, 'name': '1'}, 'letter': 'а', 'funcType': 'School', 'profileId': 1305,
        'classType': {'id': 1, 'name': 'Общеобразовательный'},
        'chiefs': [{'id': 811645, 'name': 'Туранова Людмила Александровна'}],
        'plannedOccupancy': None, 'hasClassNotWorkingTeacher': None, 'id': 105007, 'name': '1а'}
        """
        response = await self.client.get(
            url="/webapi/classes",
            params="expand=chiefs")
        return await response.json()

    async def get_report_class_attendance(self, month: int, year: int, class_id: int):
        """Получаем журнал посещаемости по классу"""
        await self.client.post(
            url="/asp/Reports/ReportClassAttendance.asp",
            data={
                'at': self.at,
                'Month': month,
                'Year': year,
                'PCLID': class_id,
                'RPNAME': 'Отчёт о посещаемости класса',
                'RPTID': 'ClassAttendance'

            }
        )

        response = await self.client.post(
            url='/asp/Reports/ClassAttendance.asp',
            data={
                'at': self.at,
            }
        )

        response_file = await self.client.get('/static/dist/pages/common/css/export-tables.min.css')
        return await response.text(), await response_file.text()

    async def get_report_teacher_average_mark(self):
        """
        Получаем отчёт "Средний балл учителя"
        Post-data params:
        "TID" - id учителя
        "TERMID" - временной промежуток
            ( -1 это "год", -2 это "итог"(но его может не быть), get_terms)
        "SJID" - предмет (-1 это "все предметы", но можно явно указать ID предмета(get_subjects)
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
        await self.client.post(
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
