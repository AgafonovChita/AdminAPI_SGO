from sgo_api.client.base import BaseClient
from sgo_api.client.admin import AdminClient
from sgo_api.client.teacher import TeacherClient

from sgo_api.utils.save_report import save_report_to_img
import config
import asyncio


URL = config.URL
USERNAME = config.USERNAME
PASSWORD = config.PASSWORD
SCHOOL_ID = config.SCHOOL_ID


async def main():
    async with AdminClient(url=URL) as client:
        await client.login(username=USERNAME, password=PASSWORD, school_id=SCHOOL_ID)

        await client.get_stuff_to_excel(name_file_export="MyExport.xls")

        await client.get_stuff()

        vocations = await client.get_vocations()
        print(vocations)

        subjects = await client.get_subjects()
        print(subjects)

        classes = await client.get_classes()
        print(classes)

        students = await client.get_students_from_class(class_id=105007)
        print(students)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
