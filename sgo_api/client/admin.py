from sgo_api.client.base import BaseClient

class AdminClient(BaseClient):
    def __init__(self, url: str):
        super().__init__(url=url)

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


