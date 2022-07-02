from sgo_api.client.base import BaseClient
from sgo_api.client.admin import AdminClient

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
        html, css = await client.get_report_teacher_average_mark()
        await save_report_to_img(html_page=html, css_file=css, name_img="Totals.jpg", size_img=(300, 400))


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
