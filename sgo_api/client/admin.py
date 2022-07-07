from sgo_api.client.teacher import TeacherClient
from sgo_api.payload import json_payload
import aiofiles


class AdminClient(TeacherClient):
    def __init__(self, url: str):
        super().__init__(url=url)

    async def get_stuff_to_excel(self, name_file_export: str = "stuff.xls"):
        """
        Получение всех работников ОУ с сохранением в файл
        :param name_file_export: имя файла отчёта для локального сохранения
        :return: None
        """
        await self.client.post(
            url="/angular/school/users/staff/",
            data={
                'at': self.at,
                'ver': self.ver,
            }
        )

        response = await self.client.post(
            url="/webapi/users/staff/registry?export=true",
            json=json_payload.json_payload_stuff
        )

        file_export_id = await response.json()

        response = await self.client.get(
            url=f"/webapi/files/{file_export_id}"
        )

        content = await response.content.read()
        async with aiofiles.open(name_file_export, "wb") as file:
            await file.write(content)

    async def get_stuff(self) -> "json":
        await self.client.post(
            url="/angular/school/users/staff/",
            data={
                'at': self.at,
                'ver': self.ver,
            }
        )

        response = await self.client.post(
            url="/webapi/users/staff/registry",
            json=json_payload.json_payload_stuff
        )

        return await response.json()
